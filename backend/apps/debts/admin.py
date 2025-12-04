from django.contrib import admin
from .models import Debt, DebtPayment


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ['name', 'debt_type', 'total_amount', 'paid_amount', 'due_date', 'is_paid', 'user']
    list_filter = ['debt_type', 'is_paid']
    search_fields = ['name', 'creditor_debtor']


@admin.register(DebtPayment)
class DebtPaymentAdmin(admin.ModelAdmin):
    list_display = ['debt', 'amount', 'payment_date']
    list_filter = ['payment_date']














