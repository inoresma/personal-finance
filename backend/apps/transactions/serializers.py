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
            user = self.context['request'].user
            
            from apps.categories.models import Category
            from django.db.models import Q
            
            if not Category.objects.filter(
                Q(id=category.id),
                Q(user=user) | Q(is_default=True, user__isnull=True)
            ).exists():
                logger.warning(f'User {user.id} attempted to use category {category.id} which is not accessible')
                raise serializers.ValidationError({
                    'category': 'La categoría seleccionada no existe o no está disponible para tu usuario.'
                })
            
            if transaction_type == 'ingreso' and category.category_type != 'ingreso':
                raise serializers.ValidationError({
                    'category': 'La categoría debe ser de tipo ingreso.'
                })
            if transaction_type == 'gasto' and category.category_type != 'gasto':
                raise serializers.ValidationError({
                    'category': 'La categoría debe ser de tipo gasto.'
                })
            
            logger.debug(f'Category validation passed: category_id={category.id}, name={category.name}, type={category.category_type}, user={category.user_id if category.user else None}, is_default={category.is_default}')
        
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
            category = validated_data.get('category')
            if category:
                from apps.categories.models import Category
                from django.db.models import Q
                user = self.context['request'].user
                
                if not Category.objects.filter(
                    Q(id=category.id),
                    Q(user=user) | Q(is_default=True, user__isnull=True)
                ).exists():
                    logger.error(f'User {user.id} attempted to create transaction with invalid category {category.id}')
                    raise serializers.ValidationError({
                        'category': 'La categoría seleccionada no existe o no está disponible para tu usuario.'
                    })
                
                logger.debug(f'Creating transaction with valid category: {category.id} ({category.name})')
            
            logger.debug(f'Creating transaction with data: {validated_data}')
            transaction = super().create(validated_data)
            logger.debug(f'Transaction created successfully: {transaction.id}')
            
            if transaction.category:
                logger.info(f'Transaction {transaction.id} created with category {transaction.category.id} ({transaction.category.name})')
        except Exception as e:
            logger.error(f'Error creating transaction: {str(e)}')
            logger.error(traceback.format_exc())
            raise serializers.ValidationError({
                'non_field_errors': f'Error al crear la transacción: {str(e)}'
            })
        
        if items_data:
            created_items = 0
            logger.info(f'Creating transaction with {len(items_data)} items, transaction_type={transaction.transaction_type}')
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
                            from apps.categories.models import Category
                            from django.db.models import Q
                            
                            try:
                                category = Category.objects.get(id=category_id)
                                
                                user = self.context['request'].user
                                if not Category.objects.filter(
                                    Q(id=category_id),
                                    Q(user=user) | Q(is_default=True, user__isnull=True)
                                ).exists():
                                    logger.warning(f'PurchaseItem {idx}: User {user.id} attempted to use category {category_id} which is not accessible')
                                    raise serializers.ValidationError({
                                        'items': f'La categoría seleccionada no existe o no está disponible para tu usuario.'
                                    })
                                
                                logger.debug(f'PurchaseItem {idx}: Validating category {category_id} ({category.name}) type={category.category_type} for transaction_type={transaction.transaction_type}')
                                if transaction.transaction_type == 'gasto' and category.category_type != 'gasto':
                                    logger.warning(f'PurchaseItem {idx}: Category {category_id} ({category.name}) is type {category.category_type}, expected "gasto" for expense transaction')
                                    raise serializers.ValidationError({
                                        'items': f'La categoría "{category.name}" debe ser de tipo gasto para esta transacción.'
                                    })
                                elif transaction.transaction_type == 'ingreso' and category.category_type != 'ingreso':
                                    logger.warning(f'PurchaseItem {idx}: Category {category_id} ({category.name}) is type {category.category_type}, expected "ingreso" for income transaction')
                                    raise serializers.ValidationError({
                                        'items': f'La categoría "{category.name}" debe ser de tipo ingreso para esta transacción.'
                                    })
                                logger.debug(f'PurchaseItem {idx}: Category validation passed')
                            except Category.DoesNotExist:
                                logger.warning(f'PurchaseItem {idx}: Category {category_id} does not exist')
                                raise serializers.ValidationError({
                                    'items': f'La categoría con ID {category_id} no existe.'
                                })
                        except (ValueError, TypeError) as e:
                            logger.warning(f'PurchaseItem {idx}: Invalid category_id format: {category_id}')
                            raise serializers.ValidationError({
                                'items': f'ID de categoría inválido: {category_id}'
                            })
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
                    logger.info(f'Created purchase item: id={purchase_item.id}, name={name}, category_id={category_id}, transaction_id={transaction.id}')
                    
                    secondary_category_ids = item_data.get('secondary_categories', [])
                    if secondary_category_ids:
                        try:
                            purchase_item.secondary_categories.set(secondary_category_ids)
                            logger.debug(f'PurchaseItem {purchase_item.id}: Set {len(secondary_category_ids)} secondary categories')
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
            logger.info(f'Updating transaction {instance.id} with {len(items_data)} items, transaction_type={instance.transaction_type}')
            
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
                            from apps.categories.models import Category
                            from django.db.models import Q
                            
                            try:
                                category = Category.objects.get(id=category_id)
                                
                                user = self.context['request'].user
                                if not Category.objects.filter(
                                    Q(id=category_id),
                                    Q(user=user) | Q(is_default=True, user__isnull=True)
                                ).exists():
                                    logger.warning(f'PurchaseItem {idx}: User {user.id} attempted to use category {category_id} which is not accessible')
                                    raise serializers.ValidationError({
                                        'items': f'La categoría seleccionada no existe o no está disponible para tu usuario.'
                                    })
                                
                                logger.debug(f'PurchaseItem {idx}: Validating category {category_id} ({category.name}) type={category.category_type} for transaction_type={instance.transaction_type}')
                                if instance.transaction_type == 'gasto' and category.category_type != 'gasto':
                                    logger.warning(f'PurchaseItem {idx}: Category {category_id} ({category.name}) is type {category.category_type}, expected "gasto" for expense transaction')
                                    raise serializers.ValidationError({
                                        'items': f'La categoría "{category.name}" debe ser de tipo gasto para esta transacción.'
                                    })
                                elif instance.transaction_type == 'ingreso' and category.category_type != 'ingreso':
                                    logger.warning(f'PurchaseItem {idx}: Category {category_id} ({category.name}) is type {category.category_type}, expected "ingreso" for income transaction')
                                    raise serializers.ValidationError({
                                        'items': f'La categoría "{category.name}" debe ser de tipo ingreso para esta transacción.'
                                    })
                                logger.debug(f'PurchaseItem {idx}: Category validation passed')
                            except Category.DoesNotExist:
                                logger.warning(f'PurchaseItem {idx}: Category {category_id} does not exist')
                                raise serializers.ValidationError({
                                    'items': f'La categoría con ID {category_id} no existe.'
                                })
                        except (ValueError, TypeError) as e:
                            logger.warning(f'PurchaseItem {idx}: Invalid category_id format: {category_id}')
                            raise serializers.ValidationError({
                                'items': f'ID de categoría inválido: {category_id}'
                            })
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
                    logger.info(f'Created purchase item: id={purchase_item.id}, name={name}, category_id={category_id}, transaction_id={instance.id}')
                    
                    secondary_category_ids = item_data.get('secondary_categories', [])
                    if secondary_category_ids:
                        try:
                            purchase_item.secondary_categories.set(secondary_category_ids)
                            logger.debug(f'PurchaseItem {purchase_item.id}: Set {len(secondary_category_ids)} secondary categories')
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
        
        category = validated_data.get('category')
        if category:
            from apps.categories.models import Category
            from django.db.models import Q
            user = self.context['request'].user
            
            if not Category.objects.filter(
                Q(id=category.id),
                Q(user=user) | Q(is_default=True, user__isnull=True)
            ).exists():
                logger.error(f'User {user.id} attempted to update transaction {instance.id} with invalid category {category.id}')
                raise serializers.ValidationError({
                    'category': 'La categoría seleccionada no existe o no está disponible para tu usuario.'
                })
            
            logger.debug(f'Updating transaction {instance.id} with valid category: {category.id} ({category.name})')
        
        transaction = super().update(instance, validated_data)
        logger.info(f'Updated transaction: id={transaction.id}, category_id={transaction.category_id}, transaction_type={transaction.transaction_type}')
        
        if transaction.category:
            logger.info(f'Transaction {transaction.id} updated with category {transaction.category.id} ({transaction.category.name})')
        else:
            logger.warning(f'Transaction {transaction.id} updated without category')
        
        if secondary_category_ids is not None:
            try:
                transaction.secondary_categories.set(secondary_category_ids)
                logger.debug(f'Transaction {transaction.id}: Set {len(secondary_category_ids)} secondary categories')
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

