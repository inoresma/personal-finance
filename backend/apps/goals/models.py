from django.db import models
from django.conf import settings
from apps.categories.models import Category
from decimal import Decimal


class Goal(models.Model):
    GOAL_TYPES = [
        ('savings', 'Meta de Ahorro'),
        ('category_reduction', 'Reducción por Categoría'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goals',
        verbose_name='Usuario'
    )
    name = models.CharField(max_length=255, verbose_name='Nombre')
    goal_type = models.CharField(
        max_length=20,
        choices=GOAL_TYPES,
        verbose_name='Tipo de Meta'
    )
    target_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Monto Objetivo'
    )
    target_date = models.DateField(verbose_name='Fecha Límite')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='goals',
        verbose_name='Categoría'
    )
    reduction_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Porcentaje de Reducción (%)'
    )
    baseline_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Monto Base'
    )
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    description = models.TextField(blank=True, verbose_name='Descripción')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Meta'
        verbose_name_plural = 'Metas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_goal_type_display()}"
    
    @property
    def current_amount(self):
        from apps.transactions.models import Transaction
        from django.db.models import Sum
        from datetime import date
        
        if self.goal_type == 'savings':
            start_date = self.created_at.date()
            end_date = min(date.today(), self.target_date)
            
            income = Transaction.objects.filter(
                user=self.user,
                transaction_type='ingreso',
                date__gte=start_date,
                date__lte=end_date
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            expenses = Transaction.objects.filter(
                user=self.user,
                transaction_type='gasto',
                date__gte=start_date,
                date__lte=end_date
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            return income - expenses
        
        elif self.goal_type == 'category_reduction' and self.category:
            start_date = self.created_at.date()
            end_date = min(date.today(), self.target_date)
            
            current_expenses = Transaction.objects.filter(
                user=self.user,
                transaction_type='gasto',
                category=self.category,
                date__gte=start_date,
                date__lte=end_date
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            if self.baseline_amount:
                return float(self.baseline_amount) - float(current_expenses)
            return Decimal('0')
        
        return Decimal('0')
    
    @property
    def progress_percentage(self):
        if self.target_amount <= 0:
            return 0
        
        current = self.current_amount
        if self.goal_type == 'category_reduction':
            if self.baseline_amount and self.baseline_amount > 0:
                reduction = float(self.baseline_amount) - float(current)
                target_reduction = float(self.target_amount)
                if target_reduction > 0:
                    return min(100, (reduction / target_reduction) * 100)
            return 0
        else:
            return min(100, (float(current) / float(self.target_amount)) * 100)
    
    @property
    def is_completed(self):
        return self.progress_percentage >= 100
    
    @property
    def days_remaining(self):
        from datetime import date
        remaining = (self.target_date - date.today()).days
        return max(0, remaining)

