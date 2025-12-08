from rest_framework import serializers
from .models import Goal
from apps.categories.serializers import CategoryListSerializer


class GoalSerializer(serializers.ModelSerializer):
    category_data = CategoryListSerializer(source='category', read_only=True)
    current_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    goal_type_display = serializers.CharField(source='get_goal_type_display', read_only=True)
    
    class Meta:
        model = Goal
        fields = [
            'id', 'name', 'goal_type', 'goal_type_display', 'target_amount',
            'target_date', 'category', 'category_data', 'reduction_percentage',
            'baseline_amount', 'is_active', 'description', 'current_amount',
            'progress_percentage', 'is_completed', 'days_remaining',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        goal_type = attrs.get('goal_type')
        category = attrs.get('category')
        reduction_percentage = attrs.get('reduction_percentage')
        baseline_amount = attrs.get('baseline_amount')
        
        if goal_type == 'category_reduction':
            if not category:
                raise serializers.ValidationError({
                    'category': 'La categoría es requerida para metas de reducción por categoría.'
                })
            if not reduction_percentage and not baseline_amount:
                raise serializers.ValidationError({
                    'reduction_percentage': 'Debe especificar un porcentaje de reducción o un monto base.'
                })
        elif goal_type == 'savings':
            if category:
                raise serializers.ValidationError({
                    'category': 'Las metas de ahorro no requieren categoría.'
                })
        
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        
        if validated_data.get('goal_type') == 'category_reduction' and not validated_data.get('baseline_amount'):
            from apps.transactions.models import Transaction
            from django.db.models import Sum
            from datetime import date
            from dateutil.relativedelta import relativedelta
            
            category = validated_data.get('category')
            if category:
                end_date = validated_data.get('target_date', date.today())
                start_date = end_date - relativedelta(months=3)
                
                baseline = Transaction.objects.filter(
                    user=validated_data['user'],
                    transaction_type='gasto',
                    category=category,
                    date__gte=start_date,
                    date__lte=end_date
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                validated_data['baseline_amount'] = baseline
        
        return super().create(validated_data)

