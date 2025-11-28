from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from .models import Budget
from .serializers import BudgetSerializer
from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionListSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'period', 'category']
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related('category')
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        budgets = self.get_queryset().filter(is_active=True)
        serializer = BudgetSerializer(budgets, many=True)
        
        alerts = []
        for budget_data in serializer.data:
            if budget_data['is_exceeded'] or budget_data['is_warning']:
                alerts.append({
                    'id': budget_data['id'],
                    'category_name': budget_data['category_name'],
                    'category_color': budget_data['category_color'],
                    'percentage': budget_data['percentage'],
                    'is_exceeded': budget_data['is_exceeded'],
                    'amount_limit': budget_data['amount_limit'],
                    'spent': budget_data['spent']
                })
        
        return Response(alerts)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        budget = self.get_object()
        budget.is_active = not budget.is_active
        budget.save()
        return Response(BudgetSerializer(budget).data)
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        budget = self.get_object()
        
        today = timezone.now().date()
        
        if budget.period == 'semanal':
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
        elif budget.period == 'mensual':
            start = today.replace(day=1)
            if today.month == 12:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        else:
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
        
        transactions = Transaction.objects.filter(
            user=request.user,
            category=budget.category,
            transaction_type='gasto',
            date__gte=start,
            date__lte=end
        ).select_related('account', 'category').order_by('-date', '-created_at')
        
        serializer = TransactionListSerializer(transactions, many=True)
        return Response(serializer.data)







