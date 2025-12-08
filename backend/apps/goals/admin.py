from django.contrib import admin
from .models import Goal


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'goal_type', 'target_amount', 'target_date', 'is_active', 'progress_percentage', 'is_completed']
    list_filter = ['goal_type', 'is_active', 'target_date']
    search_fields = ['name', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'current_amount', 'progress_percentage', 'is_completed', 'days_remaining']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'name', 'goal_type', 'description')
        }),
        ('Objetivos', {
            'fields': ('target_amount', 'target_date', 'category', 'reduction_percentage', 'baseline_amount')
        }),
        ('Estado', {
            'fields': ('is_active', 'current_amount', 'progress_percentage', 'is_completed', 'days_remaining')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )

