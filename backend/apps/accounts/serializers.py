from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'account_type', 'account_type_display', 
            'balance', 'currency', 'currency_display', 'color', 
            'icon', 'include_in_total', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'balance', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AccountBalanceUpdateSerializer(serializers.Serializer):
    initial_balance = serializers.DecimalField(max_digits=15, decimal_places=2)







