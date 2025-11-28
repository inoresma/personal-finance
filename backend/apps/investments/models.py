from django.db import models
from django.conf import settings
from apps.accounts.models import Account


class Investment(models.Model):
    INVESTMENT_TYPES = [
        ('acciones', 'Acciones'),
        ('fondos', 'Fondos de Inversión'),
        ('bonos', 'Bonos'),
        ('cripto', 'Criptomonedas'),
        ('inmuebles', 'Bienes Raíces'),
        ('deposito', 'Depósito a Plazo'),
        ('otro', 'Otro'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='investments')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPES, verbose_name='Tipo')
    initial_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Monto inicial')
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Monto actual')
    start_date = models.DateField(verbose_name='Fecha inicio')
    expected_return = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Rentabilidad esperada (%)'
    )
    account = models.ForeignKey(
        Account, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='investments',
        verbose_name='Cuenta asociada'
    )
    notes = models.TextField(blank=True, verbose_name='Notas')
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Inversión'
        verbose_name_plural = 'Inversiones'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_investment_type_display()})"
    
    @property
    def profit_loss(self):
        return self.current_amount - self.initial_amount
    
    @property
    def profit_loss_percentage(self):
        if self.initial_amount > 0:
            return ((self.current_amount - self.initial_amount) / self.initial_amount) * 100
        return 0






