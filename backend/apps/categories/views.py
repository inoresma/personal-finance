import logging
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.db import transaction

from .models import Category, SecondaryCategory
from .serializers import (
    CategorySerializer, CategoryListSerializer,
    SecondaryCategorySerializer, SecondaryCategoryListSerializer
)

logger = logging.getLogger(__name__)


class NoPagination(PageNumberPagination):
    page_size = None


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category_type', 'parent']
    pagination_class = NoPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.filter(
            Q(user=user) | Q(is_default=True, user__isnull=True)
        ).select_related('parent').prefetch_related('subcategories')
        logger.debug(f"get_queryset: usuario={user.id}, total categorías={queryset.count()}")
        logger.debug(f"get_queryset: categorías del usuario={queryset.filter(user=user).count()}")
        logger.debug(f"get_queryset: categorías predeterminadas={queryset.filter(is_default=True, user__isnull=True).count()}")
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        logger.info(f"perform_create: usuario={user.id}, email={user.email}")
        
        try:
            with transaction.atomic():
                instance = serializer.save(user=user)
                logger.info(f"perform_create: categoría creada con id={instance.id}, name={instance.name}, user={instance.user_id}, category_type={instance.category_type}")
                
                saved = Category.objects.get(id=instance.id)
                logger.info(f"perform_create: categoría guardada correctamente - id={saved.id}, name={saved.name}, user={saved.user_id}, category_type={saved.category_type}, is_default={saved.is_default}")
                
                if saved.user_id != user.id:
                    logger.error(f"perform_create: ERROR - categoría guardada con user_id={saved.user_id} pero se esperaba user_id={user.id}")
                    raise ValueError(f"Categoría no se guardó con el usuario correcto")
        except Exception as e:
            logger.error(f"perform_create: Error al crear categoría: {str(e)}", exc_info=True)
            raise
    
    def perform_destroy(self, instance):
        if instance.is_default:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('No se pueden eliminar categorías predeterminadas.')
        
        from apps.transactions.models import Transaction, PurchaseItem
        
        transactions_count = Transaction.objects.filter(category=instance).count()
        purchase_items_count = PurchaseItem.objects.filter(category=instance).count()
        
        if transactions_count > 0 or purchase_items_count > 0:
            logger.warning(f'Attempted to delete category {instance.id} ({instance.name}) which is in use: {transactions_count} transactions, {purchase_items_count} purchase items')
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                f'No se puede eliminar la categoría "{instance.name}" porque está siendo utilizada en {transactions_count + purchase_items_count} transacción(es). '
                'Primero debe actualizar o eliminar las transacciones que usan esta categoría.'
            )
        
        logger.info(f'Deleting category {instance.id} ({instance.name}) - no transactions found')
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        category_type = request.query_params.get('type', 'gasto')
        categories = self.get_queryset().filter(
            category_type=category_type, 
            parent__isnull=True
        )
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data)


class SecondaryCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = NoPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SecondaryCategoryListSerializer
        return SecondaryCategorySerializer
    
    def get_queryset(self):
        user = self.request.user
        return SecondaryCategory.objects.filter(user=user).order_by('name')
    
    def perform_create(self, serializer):
        user = self.request.user
        logger.info(f"perform_create SecondaryCategory: usuario={user.id}")
        try:
            with transaction.atomic():
                instance = serializer.save(user=user)
                logger.info(f"perform_create SecondaryCategory: categoría creada con id={instance.id}, name={instance.name}, user={instance.user_id}")
        except Exception as e:
            logger.error(f"perform_create SecondaryCategory: Error al crear categoría secundaria: {str(e)}", exc_info=True)
            raise











