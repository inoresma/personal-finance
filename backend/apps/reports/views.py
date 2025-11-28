from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
import csv
from openpyxl import Workbook
from io import BytesIO

from apps.accounts.models import Account
from apps.transactions.models import Transaction
from apps.budgets.models import Budget
from apps.investments.models import Investment
from apps.debts.models import Debt


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        account_filter = request.query_params.get('account')
        category_filter = request.query_params.get('category')
        
        accounts = Account.objects.filter(user=user, is_active=True, include_in_total=True)
        total_balance = sum(acc.balance for acc in accounts)
        
        month_transactions = Transaction.objects.filter(
            user=user,
            date__gte=month_start,
            date__lte=today
        )
        
        if account_filter:
            month_transactions = month_transactions.filter(account_id=account_filter)
        
        if category_filter:
            from apps.categories.models import Category
            cat = Category.objects.filter(id=category_filter).first()
            if cat:
                subcats = cat.subcategories.values_list('id', flat=True)
                cat_ids = [cat.id] + list(subcats)
                month_transactions = month_transactions.filter(category_id__in=cat_ids)
        
        month_income = month_transactions.filter(
            transaction_type='ingreso'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        month_expenses = month_transactions.filter(
            transaction_type='gasto'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        ant_expenses = month_transactions.filter(
            transaction_type='gasto',
            is_ant_expense=True
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        normal_expenses = month_transactions.filter(
            transaction_type='gasto',
            is_ant_expense=False
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expenses_by_account = month_transactions.filter(
            transaction_type='gasto'
        ).select_related('account').values(
            'account__id', 'account__name', 'account__color'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        expenses_by_category = month_transactions.filter(
            transaction_type='gasto',
            category__isnull=False
        ).select_related('category__parent').values(
            'category__id', 'category__name', 'category__color', 'category__icon',
            'category__parent_id', 'category__parent__name', 'category__parent__color'
        ).annotate(total=Sum('amount')).order_by('-total')[:20]
        
        recent_qs = Transaction.objects.filter(user=user)
        if account_filter:
            recent_qs = recent_qs.filter(account_id=account_filter)
        recent_transactions = recent_qs.select_related('account', 'category').order_by('-date', '-created_at')[:5]
        
        from apps.transactions.serializers import TransactionListSerializer
        recent_serialized = TransactionListSerializer(recent_transactions, many=True).data
        
        from apps.budgets.serializers import BudgetSerializer
        budget_alerts = []
        budgets = Budget.objects.filter(user=user, is_active=True).select_related('category')
        for budget in budgets:
            serializer = BudgetSerializer(budget)
            data = serializer.data
            if data['is_exceeded'] or data['is_warning']:
                budget_alerts.append({
                    'category_name': data['category_name'],
                    'category_color': data['category_color'],
                    'percentage': data['percentage'],
                    'is_exceeded': data['is_exceeded'],
                    'spent': data['spent'],
                    'limit': float(budget.amount_limit)
                })
        
        investments_total = Investment.objects.filter(
            user=user, is_active=True
        ).aggregate(total=Sum('current_amount'))['total'] or 0
        
        debts_total = Debt.objects.filter(
            user=user, is_paid=False, debt_type='deuda'
        ).aggregate(
            total=Sum('total_amount'),
            paid=Sum('paid_amount')
        )
        debts_remaining = (debts_total['total'] or 0) - (debts_total['paid'] or 0)
        
        account_stats = {}
        for acc in accounts:
            acc_transactions = Transaction.objects.filter(
                user=user,
                account=acc,
                date__gte=month_start,
                date__lte=today
            )
            account_stats[acc.id] = {
                'income': acc_transactions.filter(transaction_type='ingreso').aggregate(total=Sum('amount'))['total'] or 0,
                'expenses': acc_transactions.filter(transaction_type='gasto').aggregate(total=Sum('amount'))['total'] or 0,
            }
        
        return Response({
            'total_balance': total_balance,
            'accounts_count': accounts.count(),
            'month_summary': {
                'income': month_income,
                'expenses': month_expenses,
                'balance': month_income - month_expenses
            },
            'expenses_by_category': list(expenses_by_category),
            'recent_transactions': recent_serialized,
            'budget_alerts': budget_alerts,
            'investments_total': investments_total,
            'debts_remaining': debts_remaining,
            'account_stats': account_stats,
            'ant_expenses': {
                'ant': float(ant_expenses),
                'normal': float(normal_expenses),
                'total': float(month_expenses)
            },
            'expenses_by_account': list(expenses_by_account)
        })


class ReportsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        period = request.query_params.get('period', 'month')
        account_filter = request.query_params.get('account')
        
        today = timezone.now().date()
        
        if period == 'week':
            start_date = today - timedelta(days=7)
            trunc_func = TruncDay
        elif period == 'month':
            start_date = today - timedelta(days=30)
            trunc_func = TruncDay
        elif period == 'year':
            start_date = today - timedelta(days=365)
            trunc_func = TruncMonth
        else:
            start_date = request.query_params.get('start_date', today - timedelta(days=30))
            end_date = request.query_params.get('end_date', today)
            trunc_func = TruncDay
        
        if period != 'custom':
            end_date = today
        
        transactions = Transaction.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        if account_filter:
            transactions = transactions.filter(account_id=account_filter)
        
        income_over_time = transactions.filter(
            transaction_type='ingreso'
        ).annotate(
            period=trunc_func('date')
        ).values('period').annotate(
            total=Sum('amount')
        ).order_by('period')
        
        expenses_over_time = transactions.filter(
            transaction_type='gasto'
        ).annotate(
            period=trunc_func('date')
        ).values('period').annotate(
            total=Sum('amount')
        ).order_by('period')
        
        by_category = transactions.filter(
            transaction_type='gasto',
            category__isnull=False
        ).select_related('category__parent').values(
            'category__id', 'category__name', 'category__color',
            'category__parent_id', 'category__parent__name', 'category__parent__color'
        ).annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        totals = {
            'income': transactions.filter(transaction_type='ingreso').aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'expenses': transactions.filter(transaction_type='gasto').aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'transfers': transactions.filter(transaction_type='transferencia').aggregate(
                total=Sum('amount')
            )['total'] or 0,
        }
        totals['balance'] = totals['income'] - totals['expenses']
        
        ant_expenses = transactions.filter(
            transaction_type='gasto',
            is_ant_expense=True
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        normal_expenses = transactions.filter(
            transaction_type='gasto',
            is_ant_expense=False
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expenses_by_account = transactions.filter(
            transaction_type='gasto'
        ).select_related('account').values(
            'account__id', 'account__name', 'account__color'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        return Response({
            'period': {
                'start': start_date,
                'end': end_date,
                'type': period
            },
            'income_over_time': list(income_over_time),
            'expenses_over_time': list(expenses_over_time),
            'by_category': list(by_category),
            'totals': totals,
            'ant_expenses': {
                'ant': float(ant_expenses),
                'normal': float(normal_expenses),
                'total': float(totals['expenses'])
            },
            'expenses_by_account': list(expenses_by_account)
        })


class ExportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        format_type = request.query_params.get('format', 'csv')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        transactions = Transaction.objects.filter(user=user).select_related(
            'account', 'destination_account', 'category'
        ).order_by('-date')
        
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
        
        if format_type == 'csv':
            return self._export_csv(transactions)
        elif format_type == 'excel':
            return self._export_excel(transactions)
        else:
            return Response({'error': 'Formato no soportado'}, status=400)
    
    def _export_csv(self, transactions):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transacciones.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Fecha', 'Tipo', 'Monto', 'Descripción', 'Cuenta', 'Categoría'])
        
        for t in transactions:
            writer.writerow([
                t.date,
                t.get_transaction_type_display(),
                t.amount,
                t.description,
                t.account.name,
                t.category.name if t.category else ''
            ])
        
        return response
    
    def _export_excel(self, transactions):
        wb = Workbook()
        ws = wb.active
        ws.title = "Transacciones"
        
        headers = ['Fecha', 'Tipo', 'Monto', 'Descripción', 'Cuenta', 'Categoría', 'Notas']
        ws.append(headers)
        
        for t in transactions:
            ws.append([
                t.date.isoformat(),
                t.get_transaction_type_display(),
                float(t.amount),
                t.description,
                t.account.name,
                t.category.name if t.category else '',
                t.notes
            ])
        
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="transacciones.xlsx"'
        return response


class ImportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No se proporcionó archivo'}, status=400)
        
        if not file.name.endswith('.csv'):
            return Response({'error': 'Solo se aceptan archivos CSV'}, status=400)
        
        try:
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            imported = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    from apps.accounts.models import Account
                    from apps.categories.models import Category
                    from datetime import datetime
                    
                    account = Account.objects.filter(
                        user=request.user, 
                        name__iexact=row.get('Cuenta', '')
                    ).first()
                    
                    if not account:
                        errors.append(f"Fila {row_num}: Cuenta '{row.get('Cuenta')}' no encontrada")
                        continue
                    
                    type_map = {
                        'ingreso': 'ingreso',
                        'gasto': 'gasto',
                        'transferencia': 'transferencia'
                    }
                    transaction_type = type_map.get(row.get('Tipo', '').lower())
                    
                    if not transaction_type:
                        errors.append(f"Fila {row_num}: Tipo de transacción inválido")
                        continue
                    
                    category = None
                    if row.get('Categoría'):
                        category = Category.objects.filter(
                            name__iexact=row.get('Categoría')
                        ).filter(
                            models.Q(user=request.user) | models.Q(is_default=True)
                        ).first()
                    
                    Transaction.objects.create(
                        user=request.user,
                        transaction_type=transaction_type,
                        amount=float(row.get('Monto', 0)),
                        description=row.get('Descripción', ''),
                        date=datetime.strptime(row.get('Fecha'), '%Y-%m-%d').date(),
                        account=account,
                        category=category
                    )
                    imported += 1
                    
                except Exception as e:
                    errors.append(f"Fila {row_num}: {str(e)}")
            
            return Response({
                'imported': imported,
                'errors': errors[:10]
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)

