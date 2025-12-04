import logging
from decimal import Decimal
from rest_framework import serializers
from .models import Transaction, RecurringTransaction, PurchaseItem
from apps.accounts.serializers import AccountSerializer
from apps.categories.serializers import CategorySerializer, SecondaryCategorySerializer

logger = logging.getLogger(__name__)


class PurchaseItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    secondary_categories = SecondaryCategorySerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = PurchaseItem
        fields = [
            'id', 'name', 'amount', 'quantity', 'category', 'category_name', 
            'category_color', 'category_icon', 'secondary_categories', 'is_ant_expense', 
            'total', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    destination_account_name = serializers.CharField(source='destination_account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    secondary_categories = SecondaryCategorySerializer(many=True, read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    items = PurchaseItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display', 'amount', 
            'description', 'notes', 'date', 'account', 'account_name',
            'destination_account', 'destination_account_name', 
            'category', 'category_name', 'category_color', 'category_icon',
            'secondary_categories', 'is_recurring', 'is_ant_expense', 'related_bet', 
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'related_bet']
    
    def validate(self, attrs):
        transaction_type = attrs.get('transaction_type')
        destination_account = attrs.get('destination_account')
        account = attrs.get('account')
        category = attrs.get('category')
        amount = attrs.get('amount')
        
        logger.debug(f'Validating transaction: type={transaction_type}, account={account}, amount={amount}')
        
        # Validar que amount sea mayor a 0
        if amount is not None and amount <= 0:
            raise serializers.ValidationError({
                'amount': 'El monto debe ser mayor a 0.'
            })
        
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
        
        if transaction_type == 'ajuste':
            if destination_account:
                raise serializers.ValidationError({
                    'destination_account': 'Los ajustes no pueden tener cuenta destino.'
                })
        
        return attrs
    
    def create(self, validated_data):
        import traceback
        items_data = self.context['request'].data.get('items', [])
        validated_data['user'] = self.context['request'].user
        
        logger.debug(f'Creating transaction with {len(items_data)} items')
        logger.debug(f'Validated data keys: {list(validated_data.keys())}')
        
        secondary_category_ids = self.context['request'].data.get('secondary_categories', [])
        
        if items_data:
            try:
                total_amount = sum(
                    Decimal(str(item.get('amount', 0) or 0)) * int(item.get('quantity', 1) or 1)
                    for item in items_data
                )
                if total_amount <= 0:
                    raise serializers.ValidationError({
                        'items': 'El total de los productos debe ser mayor a 0.'
                    })
                validated_data['amount'] = total_amount
                logger.debug(f'Calculated total amount: {total_amount}')
            except (ValueError, TypeError) as e:
                logger.error(f'Error calculating total: {str(e)}')
                raise serializers.ValidationError({
                    'items': f'Error al calcular el total de los productos: {str(e)}'
                })
        
        # Asegurar que amount sea Decimal si está presente
        if 'amount' in validated_data and not isinstance(validated_data['amount'], Decimal):
            validated_data['amount'] = Decimal(str(validated_data['amount']))
        
        # Manejar related_bet de forma segura
        # Verificar si el campo existe en el modelo antes de usarlo
        try:
            if hasattr(Transaction, 'related_bet'):
                if 'related_bet' not in validated_data:
                    validated_data['related_bet'] = None
            else:
                # Si el campo no existe, eliminarlo de validated_data
                validated_data.pop('related_bet', None)
        except Exception as e:
            logger.warning(f'Error handling related_bet field: {str(e)}')
            validated_data.pop('related_bet', None)
        
        try:
            logger.debug(f'Creating transaction with data: {validated_data}')
            transaction = super().create(validated_data)
            logger.debug(f'Transaction created successfully: {transaction.id}')
        except Exception as e:
            logger.error(f'Error creating transaction: {str(e)}')
            logger.error(traceback.format_exc())
            raise serializers.ValidationError({
                'non_field_errors': f'Error al crear la transacción: {str(e)}'
            })
        
        if items_data:
            created_items = 0
            for idx, item_data in enumerate(items_data):
                try:
                    name = item_data.get('name', '').strip()
                    if not name:
                        logger.warning(f'Skipping item {idx} - no name provided')
                        continue  # Saltar items sin nombre
                    
                    amount = Decimal(str(item_data.get('amount', 0) or 0))
                    quantity = int(item_data.get('quantity', 1) or 1)
                    category_id = item_data.get('category')
                    
                    if amount <= 0:
                        logger.warning(f'Skipping item {idx} - invalid amount: {amount}')
                        continue
                    
                    if quantity <= 0:
                        logger.warning(f'Skipping item {idx} - invalid quantity: {quantity}')
                        continue
                    
                    if category_id:
                        try:
                            category_id = int(category_id)
                        except (ValueError, TypeError):
                            category_id = None
                    else:
                        category_id = None
                    
                    purchase_item = PurchaseItem.objects.create(
                        transaction=transaction,
                        name=name,
                        amount=amount,
                        quantity=quantity,
                        category_id=category_id,
                        is_ant_expense=bool(item_data.get('is_ant_expense', False))
                    )
                    
                    secondary_category_ids = item_data.get('secondary_categories', [])
                    if secondary_category_ids:
                        try:
                            purchase_item.secondary_categories.set(secondary_category_ids)
                        except Exception as e:
                            logger.warning(f'Error setting secondary categories for item {idx}: {str(e)}')
                    created_items += 1
                    logger.debug(f'Created purchase item: {name} - {quantity}x {amount}')
                except (ValueError, TypeError) as e:
                    logger.error(f'Error creating purchase item {idx}: {str(e)}')
                    continue
                except Exception as e:
                    logger.error(f'Unexpected error creating purchase item {idx}: {str(e)}')
                    logger.error(traceback.format_exc())
                    continue
            
            if created_items == 0 and len(items_data) > 0:
                logger.warning('No purchase items were created despite items_data being provided')
        
        if secondary_category_ids:
            try:
                transaction.secondary_categories.set(secondary_category_ids)
            except Exception as e:
                logger.warning(f'Error setting secondary categories: {str(e)}')
        
        return transaction
    
    def update(self, instance, validated_data):
        import traceback
        items_data = self.context['request'].data.get('items', None)
        secondary_category_ids = self.context['request'].data.get('secondary_categories', None)
        
        logger.debug(f'Updating transaction {instance.id} with {len(items_data) if items_data else 0} items')
        
        if items_data is not None:
            try:
                total_amount = sum(
                    Decimal(str(item.get('amount', 0) or 0)) * int(item.get('quantity', 1) or 1)
                    for item in items_data
                )
                if total_amount <= 0:
                    raise serializers.ValidationError({
                        'items': 'El total de los productos debe ser mayor a 0.'
                    })
                validated_data['amount'] = total_amount
                logger.debug(f'Calculated total amount: {total_amount}')
            except (ValueError, TypeError) as e:
                logger.error(f'Error calculating total: {str(e)}')
                raise serializers.ValidationError({
                    'items': f'Error al calcular el total de los productos: {str(e)}'
                })
            
            instance.items.all().delete()
            
            created_items = 0
            for idx, item_data in enumerate(items_data):
                try:
                    name = item_data.get('name', '').strip()
                    if not name:
                        logger.warning(f'Skipping item {idx} - no name provided')
                        continue  # Saltar items sin nombre
                    
                    amount = Decimal(str(item_data.get('amount', 0) or 0))
                    quantity = int(item_data.get('quantity', 1) or 1)
                    category_id = item_data.get('category')
                    is_ant_expense = bool(item_data.get('is_ant_expense', False))
                    
                    if amount <= 0:
                        logger.warning(f'Skipping item {idx} - invalid amount: {amount}')
                        continue
                    
                    if quantity <= 0:
                        logger.warning(f'Skipping item {idx} - invalid quantity: {quantity}')
                        continue
                    
                    if category_id:
                        try:
                            category_id = int(category_id)
                        except (ValueError, TypeError):
                            category_id = None
                    else:
                        category_id = None
                    
                    purchase_item = PurchaseItem.objects.create(
                        transaction=instance,
                        name=name,
                        amount=amount,
                        quantity=quantity,
                        category_id=category_id,
                        is_ant_expense=is_ant_expense
                    )
                    
                    secondary_category_ids = item_data.get('secondary_categories', [])
                    if secondary_category_ids:
                        try:
                            purchase_item.secondary_categories.set(secondary_category_ids)
                        except Exception as e:
                            logger.warning(f'Error setting secondary categories for item {idx}: {str(e)}')
                    created_items += 1
                    logger.debug(f'Created purchase item: {name} - {quantity}x {amount}')
                except (ValueError, TypeError) as e:
                    logger.error(f'Error creating purchase item {idx}: {str(e)}')
                    continue
                except Exception as e:
                    logger.error(f'Unexpected error creating purchase item {idx}: {str(e)}')
                    logger.error(traceback.format_exc())
                    continue
            
            if created_items == 0 and len(items_data) > 0:
                logger.warning('No purchase items were created despite items_data being provided')
        
        # Manejar related_bet de forma segura
        try:
            if hasattr(Transaction, 'related_bet'):
                if 'related_bet' not in validated_data:
                    validated_data['related_bet'] = None
            else:
                validated_data.pop('related_bet', None)
        except Exception as e:
            logger.warning(f'Error handling related_bet field: {str(e)}')
            validated_data.pop('related_bet', None)
        
        transaction = super().update(instance, validated_data)
        
        if secondary_category_ids is not None:
            try:
                transaction.secondary_categories.set(secondary_category_ids)
            except Exception as e:
                logger.warning(f'Error setting secondary categories: {str(e)}')
        
        return transaction


class TransactionListSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    account_color = serializers.CharField(source='account.color', read_only=True)
    destination_account_name = serializers.CharField(source='destination_account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    secondary_categories = SecondaryCategorySerializer(many=True, read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    items_count = serializers.SerializerMethodField()
    has_items = serializers.SerializerMethodField()
    items = PurchaseItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display', 'amount', 
            'description', 'date', 'account', 'account_name', 'account_color',
            'destination_account', 'destination_account_name',
            'category', 'category_name', 'category_color', 'category_icon',
            'secondary_categories', 'is_ant_expense', 'items_count', 'has_items', 'items'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def get_has_items(self, obj):
        return obj.items.exists()


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

