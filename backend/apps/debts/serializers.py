from rest_framework import serializers
from .models import Debt, DebtPayment


class DebtPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtPayment
        fields = ['id', 'amount', 'payment_date', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class DebtSerializer(serializers.ModelSerializer):
    debt_type_display = serializers.CharField(source='get_debt_type_display', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    progress_percentage = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    payments = DebtPaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Debt
        fields = [
            'id', 'name', 'debt_type', 'debt_type_display', 'total_amount',
            'paid_amount', 'remaining_amount', 'progress_percentage',
            'interest_rate', 'start_date', 'due_date', 'account', 'account_name',
            'creditor_debtor', 'notes', 'is_paid', 'payments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'paid_amount', 'is_paid', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DebtListSerializer(serializers.ModelSerializer):
    debt_type_display = serializers.CharField(source='get_debt_type_display', read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    progress_percentage = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Debt
        fields = [
            'id', 'name', 'debt_type', 'debt_type_display', 'total_amount',
            'paid_amount', 'remaining_amount', 'progress_percentage',
            'due_date', 'is_paid'
        ]

















