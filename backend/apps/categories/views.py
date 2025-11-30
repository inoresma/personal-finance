from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Category
from .serializers import CategorySerializer, CategoryListSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category_type', 'parent']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def get_queryset(self):
        user = self.request.user
        return Category.objects.filter(
            Q(user=user) | Q(is_default=True, user__isnull=True)
        ).select_related('parent').prefetch_related('subcategories')
    
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









