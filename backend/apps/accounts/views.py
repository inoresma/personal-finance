from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Account
from .serializers import AccountSerializer, AccountBalanceUpdateSerializer


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





