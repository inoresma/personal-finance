from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Category, SecondaryCategory
from .serializers import (
    CategorySerializer, CategoryListSerializer,
    SecondaryCategorySerializer, SecondaryCategoryListSerializer
)


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
        print(f"get_queryset: usuario={user.id}, total categorías={queryset.count()}")
        print(f"get_queryset: categorías del usuario={queryset.filter(user=user).count()}")
        print(f"get_queryset: categorías predeterminadas={queryset.filter(is_default=True, user__isnull=True).count()}")
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        print(f"perform_create: usuario={user.id}, email={user.email}")
        instance = serializer.save(user=user)
        print(f"perform_create: categoría creada con id={instance.id}, user={instance.user_id}, category_type={instance.category_type}")
        print(f"perform_create: verificando guardado - categoría existe={Category.objects.filter(id=instance.id).exists()}")
        if Category.objects.filter(id=instance.id).exists():
            saved = Category.objects.get(id=instance.id)
            print(f"perform_create: categoría guardada - user={saved.user_id}, category_type={saved.category_type}")
    
    def perform_destroy(self, instance):
        if instance.is_default:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('No se pueden eliminar categorías predeterminadas.')
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
        serializer.save(user=user)











