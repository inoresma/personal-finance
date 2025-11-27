from django.db import models
from django.conf import settings
from apps.accounts.models import Account
from apps.categories.models import Category


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
        ('transferencia', 'Transferencia'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPES, verbose_name='Tipo')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Monto')
    description = models.CharField(max_length=255, blank=True, verbose_name='Descripción')
    notes = models.TextField(blank=True, verbose_name='Notas')
    date = models.DateField(verbose_name='Fecha')
    
    account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='transactions',
        verbose_name='Cuenta'
    )
    destination_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='incoming_transfers',
        verbose_name='Cuenta destino'
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='transactions',
        verbose_name='Categoría'
    )
    
    is_recurring = models.BooleanField(default=False, verbose_name='Es recurrente')
    is_ant_expense = models.BooleanField(default=False, verbose_name='Gasto hormiga')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()}: {self.amount} - {self.description}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_instance = None
        
        if not is_new:
            old_instance = Transaction.objects.get(pk=self.pk)
        
        super().save(*args, **kwargs)
        
        if is_new:
            self._apply_transaction()
        elif old_instance:
            self._reverse_transaction(old_instance)
            self._apply_transaction()
    
    def delete(self, *args, **kwargs):
        self._reverse_transaction(self)
        super().delete(*args, **kwargs)
    
    def _apply_transaction(self):
        if self.transaction_type == 'ingreso':
            self.account.balance += self.amount
            self.account.save()
        elif self.transaction_type == 'gasto':
            self.account.balance -= self.amount
            self.account.save()
        elif self.transaction_type == 'transferencia':
            self.account.balance -= self.amount
            self.account.save()
            if self.destination_account:
                self.destination_account.balance += self.amount
                self.destination_account.save()
    
    def _reverse_transaction(self, instance):
        if instance.transaction_type == 'ingreso':
            instance.account.balance -= instance.amount
            instance.account.save()
        elif instance.transaction_type == 'gasto':
            instance.account.balance += instance.amount
            instance.account.save()
        elif instance.transaction_type == 'transferencia':
            instance.account.balance += instance.amount
            instance.account.save()
            if instance.destination_account:
                instance.destination_account.balance -= instance.amount
                instance.destination_account.save()


class RecurringTransaction(models.Model):
    FREQUENCY_CHOICES = [
        ('diaria', 'Diaria'),
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
        ('anual', 'Anual'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recurring_transactions')
    transaction_type = models.CharField(max_length=15, choices=Transaction.TRANSACTION_TYPES, verbose_name='Tipo')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Monto')
    description = models.CharField(max_length=255, verbose_name='Descripción')
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Cuenta')
    destination_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='recurring_incoming',
        verbose_name='Cuenta destino'
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Categoría')
    
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, verbose_name='Frecuencia')
    start_date = models.DateField(verbose_name='Fecha inicio')
    next_execution = models.DateField(verbose_name='Próxima ejecución')
    end_date = models.DateField(null=True, blank=True, verbose_name='Fecha fin')
    
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    last_executed = models.DateField(null=True, blank=True, verbose_name='Última ejecución')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Transacción Recurrente'
        verbose_name_plural = 'Transacciones Recurrentes'
        ordering = ['next_execution']
    
    def __str__(self):
        return f"{self.description} ({self.get_frequency_display()})"

