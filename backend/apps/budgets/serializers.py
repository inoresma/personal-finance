from rest_framework import serializers
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import Budget
from apps.transactions.models import Transaction


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    spent = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    is_exceeded = serializers.SerializerMethodField()
    is_warning = serializers.SerializerMethodField()
    
    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_name', 'category_color', 'category_icon',
            'amount_limit', 'period', 'period_display', 'start_date', 'end_date',
            'is_active', 'alert_threshold', 'spent', 'percentage', 'remaining',
            'is_exceeded', 'is_warning', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_period_dates(self, obj):
        today = timezone.now().date()
        
        if obj.period == 'semanal':
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
        elif obj.period == 'mensual':
            start = today.replace(day=1)
            if today.month == 12:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        else:
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
        
        return start, end
    
    def get_spent(self, obj):
        start, end = self.get_period_dates(obj)
        spent = Transaction.objects.filter(
            user=obj.user,
            category=obj.category,
            transaction_type='gasto',
            date__gte=start,
            date__lte=end
        ).aggregate(total=Sum('amount'))['total'] or 0
        return float(spent)
    
    def get_percentage(self, obj):
        spent = self.get_spent(obj)
        if obj.amount_limit > 0:
            return round((spent / float(obj.amount_limit)) * 100, 1)
        return 0
    
    def get_remaining(self, obj):
        spent = self.get_spent(obj)
        return float(obj.amount_limit) - spent
    
    def get_is_exceeded(self, obj):
        return self.get_percentage(obj) >= 100
    
    def get_is_warning(self, obj):
        percentage = self.get_percentage(obj)
        return percentage >= obj.alert_threshold and percentage < 100
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_category(self, value):
        if value.category_type != 'gasto':
            raise serializers.ValidationError('Los presupuestos solo aplican a categorías de gasto.')
        return value









