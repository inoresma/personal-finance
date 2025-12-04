from rest_framework import serializers
from .models import Investment


class InvestmentSerializer(serializers.ModelSerializer):
    investment_type_display = serializers.CharField(source='get_investment_type_display', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    profit_loss = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    profit_loss_percentage = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Investment
        fields = [
            'id', 'name', 'investment_type', 'investment_type_display',
            'initial_amount', 'current_amount', 'start_date', 'expected_return',
            'account', 'account_name', 'notes', 'is_active',
            'profit_loss', 'profit_loss_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)














