from django.db import models
from django.conf import settings
from apps.categories.models import Category


class Budget(models.Model):
    PERIOD_CHOICES = [
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('anual', 'Anual'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets', verbose_name='Categoría')
    amount_limit = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Límite')
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='mensual', verbose_name='Período')
    start_date = models.DateField(verbose_name='Fecha inicio')
    end_date = models.DateField(null=True, blank=True, verbose_name='Fecha fin')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    alert_threshold = models.IntegerField(default=80, verbose_name='Umbral de alerta (%)')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.category.name}: {self.amount_limit} ({self.get_period_display()})"





