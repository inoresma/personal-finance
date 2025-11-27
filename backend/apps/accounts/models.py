from django.db import models
from django.conf import settings


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('efectivo', 'Efectivo'),
        ('banco', 'Cuenta Bancaria'),
        ('credito', 'Tarjeta de Crédito'),
        ('debito', 'Tarjeta de Débito'),
        ('billetera', 'Billetera Digital'),
        ('inversion', 'Cuenta de Inversión'),
        ('otro', 'Otro'),
    ]
    
    CURRENCY_CHOICES = [
        ('CLP', 'Peso Chileno'),
        ('USD', 'Dólar'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, verbose_name='Tipo')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Saldo')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='CLP', verbose_name='Moneda')
    color = models.CharField(max_length=7, default='#3B82F6', verbose_name='Color')
    icon = models.CharField(max_length=50, default='wallet', verbose_name='Icono')
    include_in_total = models.BooleanField(default=True, verbose_name='Incluir en total')
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

