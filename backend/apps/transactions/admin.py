from django.contrib import admin
from .models import Transaction, RecurringTransaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'transaction_type', 'amount', 'account', 'category', 'date', 'user']
    list_filter = ['transaction_type', 'date', 'account', 'category']
    search_fields = ['description', 'notes']
    date_hierarchy = 'date'


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'transaction_type', 'amount', 'frequency', 'next_execution', 'is_active']
    list_filter = ['frequency', 'is_active', 'transaction_type']





