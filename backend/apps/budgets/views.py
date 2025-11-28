from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Budget
from .serializers import BudgetSerializer


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






