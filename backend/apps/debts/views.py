from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from .models import Debt, DebtPayment
from .serializers import DebtSerializer, DebtListSerializer, DebtPaymentSerializer


class DebtViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['debt_type', 'is_paid', 'account']
    
    def get_queryset(self):
        return Debt.objects.filter(user=self.request.user).select_related('account').prefetch_related('payments')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DebtListSerializer
        return DebtSerializer
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        queryset = self.get_queryset().filter(is_paid=False)
        
        total_owed = queryset.filter(debt_type='deuda').aggregate(
            total=Sum('total_amount'),
            paid=Sum('paid_amount')
        )
        
        total_lent = queryset.filter(debt_type='prestamo').aggregate(
            total=Sum('total_amount'),
            paid=Sum('paid_amount')
        )
        
        return Response({
            'debts': {
                'total': total_owed['total'] or 0,
                'paid': total_owed['paid'] or 0,
                'remaining': (total_owed['total'] or 0) - (total_owed['paid'] or 0)
            },
            'loans': {
                'total': total_lent['total'] or 0,
                'paid': total_lent['paid'] or 0,
                'remaining': (total_lent['total'] or 0) - (total_lent['paid'] or 0)
            }
        })
    
    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        debt = self.get_object()
        serializer = DebtPaymentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(debt=debt)
            return Response(DebtSerializer(debt).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        debt = self.get_object()
        payments = debt.payments.all()
        serializer = DebtPaymentSerializer(payments, many=True)
        return Response(serializer.data)

















