from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from .models import Account
from .serializers import AccountSerializer, AccountBalanceUpdateSerializer, AccountAdjustBalanceSerializer
from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionListSerializer
from datetime import date


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['account_type', 'currency', 'is_active']
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_initial_balance(self, request, pk=None):
        account = self.get_object()
        serializer = AccountBalanceUpdateSerializer(data=request.data)
        if serializer.is_valid():
            account.balance = serializer.validated_data['initial_balance']
            account.save()
            return Response(AccountSerializer(account).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def total_balance(self, request):
        accounts = self.get_queryset().filter(include_in_total=True, is_active=True)
        total = sum(account.balance for account in accounts)
        return Response({
            'total_balance': total,
            'accounts_count': accounts.count()
        })
    
    @action(detail=True, methods=['post'])
    def adjust_balance(self, request, pk=None):
        account = self.get_object()
        serializer = AccountAdjustBalanceSerializer(data=request.data)
        
        if serializer.is_valid():
            new_balance = serializer.validated_data['new_balance']
            description = serializer.validated_data.get('description', '')
            
            if not description:
                description = f'Ajuste de balance: {account.balance} → {new_balance}'
            
            adjustment = Transaction.objects.create(
                user=request.user,
                transaction_type='ajuste',
                amount=new_balance,
                description=description,
                date=date.today(),
                account=account
            )
            
            return Response({
                'account': AccountSerializer(account).data,
                'adjustment': TransactionListSerializer(adjustment).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        account = self.get_object()
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        transactions = Transaction.objects.filter(
            account=account,
            date__gte=month_start,
            date__lte=today
        ).exclude(transaction_type='ajuste')
        
        income = transactions.filter(transaction_type='ingreso').aggregate(total=Sum('amount'))['total'] or 0
        expenses = transactions.filter(transaction_type='gasto').aggregate(total=Sum('amount'))['total'] or 0
        transfers_out = transactions.filter(transaction_type='transferencia').aggregate(total=Sum('amount'))['total'] or 0
        
        transfers_in = Transaction.objects.filter(
            destination_account=account,
            date__gte=month_start,
            date__lte=today,
            transaction_type='transferencia'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        recent_transactions = Transaction.objects.filter(
            account=account
        ).select_related('category', 'destination_account').order_by('-date', '-created_at')[:20]
        
        serializer = TransactionListSerializer(recent_transactions, many=True)
        
        return Response({
            'account': AccountSerializer(account).data,
            'summary': {
                'income': float(income),
                'expenses': float(expenses),
                'transfers_out': float(transfers_out),
                'transfers_in': float(transfers_in),
            },
            'transactions': serializer.data
        })







