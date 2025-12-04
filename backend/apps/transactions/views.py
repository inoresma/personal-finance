from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, F
from django.db import models
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from .models import Transaction, RecurringTransaction
from .serializers import (
    TransactionSerializer, 
    TransactionListSerializer, 
    RecurringTransactionSerializer
)
from .filters import TransactionFilter


class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ['description', 'notes']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TransactionListSerializer
        return TransactionSerializer
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related(
            'account', 'destination_account', 'category'
        ).prefetch_related('items', 'items__category', 'secondary_categories', 'items__secondary_categories')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        queryset = self.get_queryset()
        
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        income = queryset.filter(transaction_type='ingreso').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        expenses = queryset.filter(transaction_type='gasto').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        return Response({
            'income': income,
            'expenses': expenses,
            'balance': income - expenses
        })
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        queryset = self.get_queryset().filter(transaction_type='gasto')
        
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        by_category = queryset.values(
            'category__id', 'category__name', 'category__color', 'category__icon'
        ).annotate(total=Sum('amount')).order_by('-total')
        
        return Response(list(by_category))
    
    @action(detail=False, methods=['get'])
    def by_secondary_category(self, request):
        from .models import PurchaseItem
        from apps.categories.models import SecondaryCategory
        
        user = request.user
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        transactions = self.get_queryset().filter(transaction_type='gasto')
        purchase_items = PurchaseItem.objects.filter(
            transaction__user=user,
            transaction__transaction_type='gasto'
        )
        
        if date_from:
            transactions = transactions.filter(date__gte=date_from)
            purchase_items = purchase_items.filter(transaction__date__gte=date_from)
        if date_to:
            transactions = transactions.filter(date__lte=date_to)
            purchase_items = purchase_items.filter(transaction__date__lte=date_to)
        
        secondary_categories_data = {}
        
        for transaction in transactions.prefetch_related('secondary_categories'):
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
        
        for item in purchase_items.prefetch_related('secondary_categories'):
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
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        limit = int(request.query_params.get('limit', 5))
        queryset = self.get_queryset()[:limit]
        serializer = TransactionListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def ant_expenses(self, request):
        from .models import PurchaseItem
        
        today = date.today()
        
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            date_from = date.fromisoformat(date_from)
        else:
            date_from = today.replace(day=1)
            
        if date_to:
            date_to = date.fromisoformat(date_to)
        else:
            date_to = today
        
        period_days = (date_to - date_from).days + 1
        prev_date_from = date_from - timedelta(days=period_days)
        prev_date_to = date_from - timedelta(days=1)
        
        current_month_transactions = self.get_queryset().filter(
            is_ant_expense=True,
            transaction_type='gasto',
            date__gte=date_from,
            date__lte=date_to
        )
        
        prev_month_transactions = self.get_queryset().filter(
            is_ant_expense=True,
            transaction_type='gasto',
            date__gte=prev_date_from,
            date__lte=prev_date_to
        )
        
        current_month_items = PurchaseItem.objects.filter(
            transaction__user=request.user,
            is_ant_expense=True,
            transaction__transaction_type='gasto',
            transaction__date__gte=date_from,
            transaction__date__lte=date_to
        )
        
        prev_month_items = PurchaseItem.objects.filter(
            transaction__user=request.user,
            is_ant_expense=True,
            transaction__transaction_type='gasto',
            transaction__date__gte=prev_date_from,
            transaction__date__lte=prev_date_to
        )
        
        current_transactions_total = current_month_transactions.aggregate(total=Sum('amount'))['total'] or 0
        current_transactions_total = float(current_transactions_total) if current_transactions_total is not None else 0.0
        current_items_total = sum(
            float(item.amount) * int(item.quantity) 
            for item in current_month_items
        )
        
        prev_transactions_total = prev_month_transactions.aggregate(total=Sum('amount'))['total'] or 0
        prev_transactions_total = float(prev_transactions_total) if prev_transactions_total is not None else 0.0
        prev_items_total = sum(
            float(item.amount) * int(item.quantity) 
            for item in prev_month_items
        )
        
        current_total = current_transactions_total + current_items_total
        prev_total = prev_transactions_total + prev_items_total
        
        current_count = current_month_transactions.count()
        transactions_with_items = current_month_items.values_list('transaction_id', flat=True).distinct()
        transactions_not_counted = transactions_with_items.exclude(
            id__in=current_month_transactions.values_list('id', flat=True)
        )
        current_count += transactions_not_counted.count()
        
        recent_transaction_ids = list(current_month_transactions.values_list('id', flat=True))
        recent_transaction_ids.extend(list(transactions_with_items))
        recent_transaction_ids = list(set(recent_transaction_ids))
        
        recent = self.get_queryset().filter(id__in=recent_transaction_ids).order_by('-date')[:5]
        serializer = TransactionListSerializer(recent, many=True)
        
        return Response({
            'current_month_total': current_total,
            'current_month_count': current_count,
            'previous_month_total': prev_total,
            'recent_ant_expenses': serializer.data
        })


class RecurringTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = RecurringTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'frequency', 'transaction_type']
    
    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user).select_related(
            'account', 'category'
        )
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save()
        return Response(RecurringTransactionSerializer(instance).data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        queryset = self.get_queryset().filter(
            is_active=True,
            next_execution__gte=date.today()
        ).order_by('next_execution')[:10]
        serializer = RecurringTransactionSerializer(queryset, many=True)
        return Response(serializer.data)

