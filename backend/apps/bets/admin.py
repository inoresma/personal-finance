from django.contrib import admin
from .models import Bet


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ['event_name', 'bet_type', 'bet_amount', 'result', 'net_result', 'date', 'user']
    list_filter = ['bet_type', 'result', 'date', 'sport_type']
    search_fields = ['event_name', 'notes', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'net_result', 'is_winning']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Información básica', {
            'fields': ('user', 'bet_type', 'event_name', 'sport_type', 'date')
        }),
        ('Detalles de la apuesta', {
            'fields': ('bet_amount', 'odds', 'result', 'payout_amount', 'account')
        }),
        ('Resultados', {
            'fields': ('net_result', 'is_winning')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )






