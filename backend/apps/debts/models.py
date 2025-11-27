from django.db import models
from django.conf import settings
from apps.accounts.models import Account


class Debt(models.Model):
    DEBT_TYPES = [
        ('deuda', 'Deuda (Debo)'),
        ('prestamo', 'Préstamo (Me deben)'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='debts')
    name = models.CharField(max_length=200, verbose_name='Nombre/Descripción')
    debt_type = models.CharField(max_length=10, choices=DEBT_TYPES, verbose_name='Tipo')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Monto total')
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Monto pagado')
    interest_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Tasa de interés (%)'
    )
    start_date = models.DateField(verbose_name='Fecha inicio')
    due_date = models.DateField(null=True, blank=True, verbose_name='Fecha vencimiento')
    account = models.ForeignKey(
        Account, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='debts',
        verbose_name='Cuenta asociada'
    )
    creditor_debtor = models.CharField(max_length=200, blank=True, verbose_name='Acreedor/Deudor')
    notes = models.TextField(blank=True, verbose_name='Notas')
    is_paid = models.BooleanField(default=False, verbose_name='Pagada')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Deuda'
        verbose_name_plural = 'Deudas'
        ordering = ['due_date', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.total_amount}"
    
    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount
    
    @property
    def progress_percentage(self):
        if self.total_amount > 0:
            return (self.paid_amount / self.total_amount) * 100
        return 0


class DebtPayment(models.Model):
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Monto')
    payment_date = models.DateField(verbose_name='Fecha de pago')
    notes = models.CharField(max_length=255, blank=True, verbose_name='Notas')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Pago de Deuda'
        verbose_name_plural = 'Pagos de Deudas'
        ordering = ['-payment_date']
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.debt.paid_amount += self.amount
            if self.debt.paid_amount >= self.debt.total_amount:
                self.debt.is_paid = True
            self.debt.save()
    
    def delete(self, *args, **kwargs):
        self.debt.paid_amount -= self.amount
        if self.debt.paid_amount < self.debt.total_amount:
            self.debt.is_paid = False
        self.debt.save()
        super().delete(*args, **kwargs)





