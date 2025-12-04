import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict

from apps.transactions.models import Transaction, PurchaseItem
from apps.transactions.serializers import TransactionListSerializer
from apps.accounts.models import Account
from apps.budgets.models import Budget
from apps.investments.models import Investment
from apps.debts.models import Debt
from apps.categories.models import SecondaryCategory

logger = logging.getLogger(__name__)


class ReportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        today = date.today()
        
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        account_id = request.query_params.get('account')
        category_id = request.query_params.get('category')
        transaction_type = request.query_params.get('transaction_type')
        
        logger.info(f'Dashboard request - User: {user.id}, date_from: {date_from}, date_to: {date_to}')
        
        if not date_from:
            month_start = today.replace(day=1)
            date_from = month_start
        else:
            date_from = date.fromisoformat(date_from)
            
        if not date_to:
            date_to = today
        else:
            date_to = date.fromisoformat(date_to)
        
        logger.info(f'Dashboard request - Parsed dates: date_from={date_from}, date_to={date_to}')
        
        transactions = Transaction.objects.filter(
            user=user,
            date__gte=date_from,
            date__lte=date_to
        ).exclude(transaction_type='ajuste').select_related('account', 'category', 'destination_account')
        
        total_transactions_count = transactions.count()
        logger.info(f'Dashboard request - Total transactions found: {total_transactions_count}')
        
        if account_id:
            transactions = transactions.filter(account_id=account_id)
        if category_id:
            transactions = transactions.filter(category_id=category_id)
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
        
        try:
            income_transactions = transactions.filter(transaction_type='ingreso')
            income_count = income_transactions.count()
            logger.info(f'Dashboard request - Income transactions: {income_count}')
            income_result = income_transactions.aggregate(
                total=Sum('amount')
            )
            income = income_result['total']
            if income is None:
                income = 0.0
            else:
                income = float(income)
            logger.info(f'Dashboard request - Total income: {income}')
        except Exception as e:
            logger.error(f'Error calculating income: {str(e)}', exc_info=True)
            income = 0.0
        
        try:
            expenses_transactions = transactions.filter(transaction_type='gasto')
            expenses_count = expenses_transactions.count()
            logger.info(f'Dashboard request - Expense transactions: {expenses_count}')
            expenses_result = expenses_transactions.aggregate(
                total=Sum('amount')
            )
            expenses = expenses_result['total']
            if expenses is None:
                expenses = 0.0
            else:
                expenses = float(expenses)
            logger.info(f'Dashboard request - Total expenses: {expenses}')
        except Exception as e:
            logger.error(f'Error calculating expenses: {str(e)}', exc_info=True)
            expenses = 0.0
        
        try:
            ant_expenses_transactions = transactions.filter(
                transaction_type='gasto',
                is_ant_expense=True
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0
            ant_expenses_transactions = float(ant_expenses_transactions) if ant_expenses_transactions is not None else 0.0
        except Exception as e:
            logger.error(f'Error calculating ant_expenses_transactions: {str(e)}', exc_info=True)
            ant_expenses_transactions = 0.0
        
        ant_expenses_items_total = 0
        try:
            ant_expenses_items = PurchaseItem.objects.filter(
                transaction__user=user,
                is_ant_expense=True,
                transaction__transaction_type='gasto',
                transaction__date__gte=date_from,
                transaction__date__lte=date_to
            ).select_related('transaction')
            
            if account_id:
                ant_expenses_items = ant_expenses_items.filter(transaction__account_id=account_id)
            if category_id:
                ant_expenses_items = ant_expenses_items.filter(category_id=category_id)
            
            for item in ant_expenses_items:
                try:
                    amount = float(item.amount) if item.amount is not None else 0.0
                    quantity = int(item.quantity) if item.quantity is not None else 1
                    ant_expenses_items_total += amount * quantity
                except (ValueError, TypeError) as e:
                    logger.warning(f'Error processing PurchaseItem {item.id}: {str(e)}')
                    continue
        except Exception as e:
            logger.error(f'Error calculating ant_expenses_items_total: {str(e)}', exc_info=True)
            ant_expenses_items_total = 0
        
        ant_expenses = ant_expenses_transactions + ant_expenses_items_total
        
        try:
            normal_expenses = expenses - ant_expenses
            normal_expenses = float(normal_expenses) if normal_expenses is not None else 0.0
        except Exception as e:
            logger.error(f'Error calculating normal_expenses: {str(e)}', exc_info=True)
            normal_expenses = 0.0
        
        expense_transactions = transactions.filter(transaction_type='gasto')
        
        purchase_items = PurchaseItem.objects.filter(
            transaction__user=user,
            transaction__transaction_type='gasto',
            transaction__date__gte=date_from,
            transaction__date__lte=date_to,
            category__isnull=False
        ).select_related('transaction', 'category', 'category__parent')
        
        if account_id:
            purchase_items = purchase_items.filter(transaction__account_id=account_id)
        if category_id:
            purchase_items = purchase_items.filter(category_id=category_id)
        
        items_by_category = {}
        transactions_with_items_ids = set()
        
        for item in purchase_items:
            category = item.category
            if category:
                category_id = category.id
                item_total = float(item.amount) * int(item.quantity)
                transactions_with_items_ids.add(item.transaction_id)
                
                if category_id not in items_by_category:
                    items_by_category[category_id] = {
                        'category__id': category_id,
                        'category__name': category.name,
                        'category__color': category.color,
                        'category__icon': category.icon,
                        'category__parent_id': category.parent_id if category.parent else None,
                        'category__parent__name': category.parent.name if category.parent else None,
                        'category__parent__color': category.parent.color if category.parent else None,
                        'total': 0.0
                    }
                items_by_category[category_id]['total'] += item_total
        
        transactions_without_items = expense_transactions.exclude(id__in=transactions_with_items_ids)
        if account_id:
            transactions_without_items = transactions_without_items.filter(account_id=account_id)
        if category_id:
            transactions_without_items = transactions_without_items.filter(category_id=category_id)
        
        transactions_by_category = transactions_without_items.filter(
            category__isnull=False
        ).values(
            'category__id',
            'category__name',
            'category__color',
            'category__icon',
            'category__parent_id',
            'category__parent__name',
            'category__parent__color'
        ).annotate(
            total=Sum('amount')
        )
        
        for trans_cat in transactions_by_category:
            cat_id = trans_cat['category__id']
            trans_total = float(trans_cat['total'])
            
            if cat_id not in items_by_category:
                items_by_category[cat_id] = {
                    'category__id': cat_id,
                    'category__name': trans_cat['category__name'],
                    'category__color': trans_cat['category__color'],
                    'category__icon': trans_cat['category__icon'],
                    'category__parent_id': trans_cat['category__parent_id'],
                    'category__parent__name': trans_cat['category__parent__name'],
                    'category__parent__color': trans_cat['category__parent__color'],
                    'total': 0.0
                }
            items_by_category[cat_id]['total'] += trans_total
        
        expenses_by_category = sorted(
            items_by_category.values(),
            key=lambda x: x['total'],
            reverse=True
        )
        
        expenses_by_account = transactions.filter(
            transaction_type='gasto'
        ).values(
            'account__id',
            'account__name',
            'account__color'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        account_stats = {}
        if not account_id:
            accounts = Account.objects.filter(user=user, is_active=True)
            for acc in accounts:
                acc_transactions = transactions.filter(account=acc)
                acc_income_result = acc_transactions.filter(transaction_type='ingreso').aggregate(
                    total=Sum('amount')
                )
                acc_income = acc_income_result['total']
                if acc_income is None:
                    acc_income = 0.0
                else:
                    acc_income = float(acc_income)
                
                acc_expenses_result = acc_transactions.filter(transaction_type='gasto').aggregate(
                    total=Sum('amount')
                )
                acc_expenses = acc_expenses_result['total']
                if acc_expenses is None:
                    acc_expenses = 0.0
                else:
                    acc_expenses = float(acc_expenses)
                
                account_stats[acc.id] = {
                    'income': acc_income,
                    'expenses': acc_expenses
                }
        
        total_balance = 0
        if not account_id:
            accounts = Account.objects.filter(
                user=user,
                include_in_total=True,
                is_active=True
            )
            total_balance = sum(float(acc.balance) if acc.balance is not None else 0.0 for acc in accounts)
        
        recent_transactions = transactions.order_by('-date', '-created_at')[:10]
        
        budget_alerts = []
        if not account_id and not category_id:
            budgets = Budget.objects.filter(
                user=user,
                is_active=True
            ).select_related('category')
            
            for budget in budgets:
                budget_transactions = transactions.filter(
                    transaction_type='gasto',
                    category=budget.category
                )
                spent = budget_transactions.aggregate(
                    total=Sum('amount')
                )['total'] or 0
                
                percentage = 0
                if budget.amount_limit > 0:
                    percentage = (spent / budget.amount_limit) * 100
                
                if percentage >= budget.alert_threshold:
                    budget_alerts.append({
                        'id': budget.id,
                        'category': budget.category.name,
                        'limit': float(budget.amount_limit),
                        'spent': float(spent),
                        'percentage': round(percentage, 2),
                        'period': budget.period
                    })
        
        investments_total = 0
        if not account_id:
            investments = Investment.objects.filter(
                user=user,
                is_active=True
            )
            investments_total = sum(inv.current_amount for inv in investments)
        
        debts_remaining = 0
        if not account_id:
            debts = Debt.objects.filter(
                user=user,
                is_paid=False
            )
            debts_remaining = sum(debt.remaining_amount for debt in debts)
        
        monthly_trends = []
        if not account_id and not category_id:
            current_date = date_from
            months_data = []
            while current_date <= date_to:
                month_start = current_date.replace(day=1)
                if current_date.month == 12:
                    month_end = date(current_date.year + 1, 1, 1) - timedelta(days=1)
                else:
                    month_end = date(current_date.year, current_date.month + 1, 1) - timedelta(days=1)
                
                month_transactions = Transaction.objects.filter(
                    user=user,
                    date__gte=month_start,
                    date__lte=min(month_end, date_to)
                ).exclude(transaction_type='ajuste')
                
                month_income_result = month_transactions.filter(
                    transaction_type='ingreso'
                ).aggregate(total=Sum('amount'))
                month_income = month_income_result['total']
                if month_income is None:
                    month_income = 0.0
                else:
                    month_income = float(month_income)
                
                month_expenses_result = month_transactions.filter(
                    transaction_type='gasto'
                ).aggregate(total=Sum('amount'))
                month_expenses = month_expenses_result['total']
                if month_expenses is None:
                    month_expenses = 0.0
                else:
                    month_expenses = float(month_expenses)
                
                months_data.append({
                    'month': month_start.strftime('%Y-%m'),
                    'month_label': month_start.strftime('%b %Y'),
                    'income': month_income,
                    'expenses': month_expenses
                })
                
                if current_date.month == 12:
                    current_date = date(current_date.year + 1, 1, 1)
                else:
                    current_date = date(current_date.year, current_date.month + 1, 1)
            
            monthly_trends = months_data[-12:]
        
        daily_expenses = []
        if not account_id and not category_id:
            current_date = date_from
            while current_date <= date_to:
                day_expenses_result = transactions.filter(
                    transaction_type='gasto',
                    date=current_date
                ).aggregate(total=Sum('amount'))
                day_expenses = day_expenses_result['total']
                if day_expenses is None:
                    day_expenses = 0.0
                else:
                    day_expenses = float(day_expenses)
                
                daily_expenses.append({
                    'date': current_date.isoformat(),
                    'day': current_date.day,
                    'day_name': current_date.strftime('%a'),
                    'total': day_expenses
                })
                current_date += timedelta(days=1)
        
        try:
            balance = income - expenses
            balance = float(balance) if balance is not None else 0.0
        except Exception as e:
            logger.error(f'Error calculating balance: {str(e)}', exc_info=True)
            balance = 0.0
        
        try:
            response_data = {
                'total_balance': float(total_balance) if total_balance is not None else 0.0,
                'month_summary': {
                    'income': float(income) if income is not None else 0.0,
                    'expenses': float(expenses) if expenses is not None else 0.0,
                    'balance': float(balance) if balance is not None else 0.0
                },
                'ant_expenses': {
                    'ant': float(ant_expenses) if ant_expenses is not None else 0.0,
                    'normal': float(normal_expenses) if normal_expenses is not None else 0.0,
                    'total': float(expenses) if expenses is not None else 0.0
                },
                'expenses_by_category': list(expenses_by_category),
                'expenses_by_account': list(expenses_by_account),
                'account_stats': account_stats,
                'recent_transactions': TransactionListSerializer(recent_transactions, many=True).data,
                'budget_alerts': budget_alerts,
                'investments_total': float(investments_total) if investments_total is not None else 0.0,
                'debts_remaining': float(debts_remaining) if debts_remaining is not None else 0.0,
                'monthly_trends': monthly_trends,
                'daily_expenses': daily_expenses
            }
            logger.info(f'Dashboard response - total_balance: {response_data["total_balance"]}, income: {response_data["month_summary"]["income"]}, expenses: {response_data["month_summary"]["expenses"]}')
            return Response(response_data)
        except Exception as e:
            logger.error(f'Error building response: {str(e)}', exc_info=True)
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'error': 'Error al calcular estadísticas del dashboard',
                'detail': str(e),
                'total_balance': 0.0,
                'month_summary': {
                    'income': 0.0,
                    'expenses': 0.0,
                    'balance': 0.0
                }
            }, status=500)


class SecondaryCategoryReportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        today = date.today()
        
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        account_id = request.query_params.get('account')
        
        if not date_from:
            month_start = today.replace(day=1)
            date_from = month_start
        else:
            date_from = date.fromisoformat(date_from)
            
        if not date_to:
            date_to = today
        else:
            date_to = date.fromisoformat(date_to)
        
        transactions = Transaction.objects.filter(
            user=user,
            transaction_type='gasto',
            date__gte=date_from,
            date__lte=date_to
        ).prefetch_related('secondary_categories')
        
        purchase_items = PurchaseItem.objects.filter(
            transaction__user=user,
            transaction__transaction_type='gasto',
            transaction__date__gte=date_from,
            transaction__date__lte=date_to
        ).prefetch_related('secondary_categories')
        
        if account_id:
            transactions = transactions.filter(account_id=account_id)
            purchase_items = purchase_items.filter(transaction__account_id=account_id)
        
        secondary_categories_data = {}
        
        for transaction in transactions:
            for sec_cat in transaction.secondary_categories.all():
                sec_cat_id = sec_cat.id
                if sec_cat_id not in secondary_categories_data:
                    secondary_categories_data[sec_cat_id] = {
                        'secondary_category__id': sec_cat_id,
                        'secondary_category__name': sec_cat.name,
                        'secondary_category__color': sec_cat.color,
                        'secondary_category__icon': sec_cat.icon,
                        'total': 0.0
                    }
                secondary_categories_data[sec_cat_id]['total'] += float(transaction.amount)
        
        for item in purchase_items:
            for sec_cat in item.secondary_categories.all():
                sec_cat_id = sec_cat.id
                item_total = float(item.amount) * int(item.quantity)
                if sec_cat_id not in secondary_categories_data:
                    secondary_categories_data[sec_cat_id] = {
                        'secondary_category__id': sec_cat_id,
                        'secondary_category__name': sec_cat.name,
                        'secondary_category__color': sec_cat.color,
                        'secondary_category__icon': sec_cat.icon,
                        'total': 0.0
                    }
                secondary_categories_data[sec_cat_id]['total'] += item_total
        
        result = sorted(
            secondary_categories_data.values(),
            key=lambda x: x['total'],
            reverse=True
        )
        
        return Response(result)
