from django.contrib import admin
from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount_limit', 'period', 'is_active', 'user']
    list_filter = ['period', 'is_active']







