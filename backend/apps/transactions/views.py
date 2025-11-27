from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count
from datetime import date
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
        )
    
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
    def recent(self, request):
        limit = int(request.query_params.get('limit', 5))
        queryset = self.get_queryset()[:limit]
        serializer = TransactionListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def ant_expenses(self, request):
        today = date.today()
        month_start = today.replace(day=1)
        prev_month_start = (month_start - relativedelta(months=1))
        prev_month_end = month_start - relativedelta(days=1)
        
        current_month = self.get_queryset().filter(
            is_ant_expense=True,
            transaction_type='gasto',
            date__gte=month_start,
            date__lte=today
        )
        
        prev_month = self.get_queryset().filter(
            is_ant_expense=True,
            transaction_type='gasto',
            date__gte=prev_month_start,
            date__lte=prev_month_end
        )
        
        current_total = current_month.aggregate(total=Sum('amount'))['total'] or 0
        current_count = current_month.count()
        prev_total = prev_month.aggregate(total=Sum('amount'))['total'] or 0
        
        recent = current_month.order_by('-date')[:5]
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

