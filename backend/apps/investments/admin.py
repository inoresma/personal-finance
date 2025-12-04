from django.contrib import admin
from .models import Investment


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'investment_type', 'initial_amount', 'current_amount', 'user', 'is_active']
    list_filter = ['investment_type', 'is_active']
    search_fields = ['name']














