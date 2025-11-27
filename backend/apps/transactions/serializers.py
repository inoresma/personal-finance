from rest_framework import serializers
from .models import Transaction, RecurringTransaction
from apps.accounts.serializers import AccountSerializer
from apps.categories.serializers import CategorySerializer


class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    destination_account_name = serializers.CharField(source='destination_account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display', 'amount', 
            'description', 'notes', 'date', 'account', 'account_name',
            'destination_account', 'destination_account_name', 
            'category', 'category_name', 'category_color', 'category_icon',
            'is_recurring', 'is_ant_expense', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        transaction_type = attrs.get('transaction_type')
        destination_account = attrs.get('destination_account')
        account = attrs.get('account')
        category = attrs.get('category')
        
        if transaction_type == 'transferencia':
            if not destination_account:
                raise serializers.ValidationError({
                    'destination_account': 'La cuenta destino es requerida para transferencias.'
                })
            if account == destination_account:
                raise serializers.ValidationError({
                    'destination_account': 'La cuenta destino debe ser diferente a la cuenta origen.'
                })
        
        if transaction_type in ['ingreso', 'gasto'] and category:
            if transaction_type == 'ingreso' and category.category_type != 'ingreso':
                raise serializers.ValidationError({
                    'category': 'La categoría debe ser de tipo ingreso.'
                })
            if transaction_type == 'gasto' and category.category_type != 'gasto':
                raise serializers.ValidationError({
                    'category': 'La categoría debe ser de tipo gasto.'
                })
        
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TransactionListSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    account_color = serializers.CharField(source='account.color', read_only=True)
    destination_account_name = serializers.CharField(source='destination_account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display', 'amount', 
            'description', 'date', 'account', 'account_name', 'account_color',
            'destination_account', 'destination_account_name',
            'category', 'category_name', 'category_color', 'category_icon',
            'is_ant_expense'
        ]


class RecurringTransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = RecurringTransaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display', 'amount',
            'description', 'account', 'account_name', 'destination_account',
            'category', 'category_name', 'frequency', 'frequency_display',
            'start_date', 'next_execution', 'end_date', 'is_active',
            'last_executed', 'created_at'
        ]
        read_only_fields = ['id', 'last_executed', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        if 'next_execution' not in validated_data:
            validated_data['next_execution'] = validated_data['start_date']
        return super().create(validated_data)

