from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from .models import Investment
from .serializers import InvestmentSerializer


class InvestmentViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['investment_type', 'is_active', 'account']
    
    def get_queryset(self):
        return Investment.objects.filter(user=self.request.user).select_related('account')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        queryset = self.get_queryset().filter(is_active=True)
        
        total_initial = queryset.aggregate(total=Sum('initial_amount'))['total'] or 0
        total_current = queryset.aggregate(total=Sum('current_amount'))['total'] or 0
        total_profit = total_current - total_initial
        
        percentage = 0
        if total_initial > 0:
            percentage = ((total_current - total_initial) / total_initial) * 100
        
        by_type = queryset.values('investment_type').annotate(
            total=Sum('current_amount')
        ).order_by('-total')
        
        return Response({
            'total_invested': total_initial,
            'total_current': total_current,
            'total_profit_loss': total_profit,
            'percentage': round(percentage, 2),
            'by_type': list(by_type),
            'count': queryset.count()
        })
    
    @action(detail=True, methods=['post'])
    def update_value(self, request, pk=None):
        investment = self.get_object()
        new_value = request.data.get('current_amount')
        
        if new_value is not None:
            investment.current_amount = new_value
            investment.save()
            return Response(InvestmentSerializer(investment).data)
        
        return Response({'error': 'current_amount es requerido'}, status=400)














