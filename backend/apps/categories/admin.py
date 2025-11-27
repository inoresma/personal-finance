from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'parent', 'user', 'is_default']
    list_filter = ['category_type', 'is_default']
    search_fields = ['name']





