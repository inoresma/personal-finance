from rest_framework import serializers
from .models import Category


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'icon']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)
    category_type_display = serializers.CharField(source='get_category_type_display', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'category_type', 'category_type_display',
            'color', 'icon', 'parent', 'is_default', 'subcategories', 'created_at'
        ]
        read_only_fields = ['id', 'is_default', 'created_at']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
    def validate_parent(self, value):
        if value and value.parent:
            raise serializers.ValidationError('No se permiten subcategorías anidadas.')
        return value


class CategoryListSerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)
    category_type_display = serializers.CharField(source='get_category_type_display', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'category_type', 'category_type_display',
            'color', 'icon', 'parent', 'parent_name', 'is_default', 'subcategories'
        ]






