from django.db import models
from django.conf import settings
from apps.accounts.models import Account


class Bet(models.Model):
    BET_TYPES = [
        ('deportes', 'Deportes'),
        ('blackjack', 'Blackjack'),
        ('poker', 'Poker'),
        ('ruleta', 'Ruleta'),
        ('tragamonedas', 'Tragamonedas'),
        ('otros', 'Otros'),
    ]
    
    RESULT_CHOICES = [
        ('ganó', 'Ganó'),
        ('perdió', 'Perdió'),
        ('pendiente', 'Pendiente'),
    ]
    
    SPORT_TYPES = [
        ('futbol', 'Fútbol'),
        ('basquet', 'Básquetbol'),
        ('tenis', 'Tenis'),
        ('beisbol', 'Béisbol'),
        ('futbol_americano', 'Fútbol Americano'),
        ('hockey', 'Hockey'),
        ('boxeo', 'Boxeo'),
        ('mma', 'MMA'),
        ('otros', 'Otros'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bets')
    bet_type = models.CharField(max_length=20, choices=BET_TYPES, verbose_name='Tipo de apuesta')
    event_name = models.CharField(max_length=255, verbose_name='Evento/Descripción')
    sport_type = models.CharField(
        max_length=20, 
        choices=SPORT_TYPES, 
        null=True, 
        blank=True,
        verbose_name='Tipo de deporte'
    )
    bet_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Monto apostado')
    odds = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Cuota/Odds'
    )
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, default='pendiente', verbose_name='Resultado')
    payout_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        verbose_name='Monto ganado'
    )
    account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='bets',
        verbose_name='Cuenta'
    )
    date = models.DateField(verbose_name='Fecha')
    notes = models.TextField(blank=True, verbose_name='Notas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Apuesta'
        verbose_name_plural = 'Apuestas'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.event_name} - {self.bet_amount} ({self.get_result_display()})"
    
    @property
    def net_result(self):
        if self.result == 'ganó':
            return self.payout_amount - self.bet_amount
        elif self.result == 'perdió':
            return -self.bet_amount
        return 0
    
    @property
    def is_winning(self):
        return self.result == 'ganó'
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_instance = None
        
        if not is_new:
            try:
                old_instance = Bet.objects.get(pk=self.pk)
            except Bet.DoesNotExist:
                old_instance = None
        
        super().save(*args, **kwargs)
        
        if is_new:
            # No llamamos _apply_bet() porque las transacciones automáticas ya modifican el saldo
            self._create_transactions()
        elif old_instance:
            # Revertir transacciones antiguas (esto también revierte el saldo)
            self._update_transactions(old_instance)
    
    def delete(self, *args, **kwargs):
        # Eliminar transacciones (esto también revierte el saldo automáticamente)
        self._delete_transactions()
        super().delete(*args, **kwargs)
    
    def _apply_bet(self):
        if self.result == 'ganó':
            self.account.balance -= self.bet_amount
            self.account.balance += self.payout_amount
        elif self.result == 'perdió':
            self.account.balance -= self.bet_amount
        elif self.result == 'pendiente':
            self.account.balance -= self.bet_amount
        self.account.save()
    
    def _reverse_bet(self, instance):
        if instance.result == 'ganó':
            instance.account.balance += instance.bet_amount
            instance.account.balance -= instance.payout_amount
        elif instance.result == 'perdió':
            instance.account.balance += instance.bet_amount
        elif instance.result == 'pendiente':
            instance.account.balance += instance.bet_amount
        instance.account.save()
    
    def _create_transactions(self):
        from apps.transactions.models import Transaction
        
        if self.result == 'ganó':
            # Si ganó, solo crear una transacción de ingreso con la ganancia neta
            # Ganancia neta = monto ganado - monto apostado
            net_profit = self.payout_amount - self.bet_amount
            Transaction.objects.create(
                user=self.user,
                transaction_type='ingreso',
                amount=net_profit,
                description=f"Ganancia de apuesta: {self.event_name}",
                date=self.date,
                account=self.account,
                related_bet=self,
                notes=f"Ganancia neta de apuesta {self.get_bet_type_display()} (Ganado: {self.payout_amount} - Apostado: {self.bet_amount})"
            )
        elif self.result == 'perdió':
            # Si perdió, crear transacción de gasto (monto apostado)
            Transaction.objects.create(
                user=self.user,
                transaction_type='gasto',
                amount=self.bet_amount,
                description=f"Apuesta perdida: {self.event_name}",
                date=self.date,
                account=self.account,
                related_bet=self,
                notes=f"Apuesta {self.get_bet_type_display()}" + (f" - {self.get_sport_type_display()}" if self.sport_type else "")
            )
        elif self.result == 'pendiente':
            # Si está pendiente, crear transacción de gasto (monto apostado)
            # Cuando se resuelva, se actualizará automáticamente
            Transaction.objects.create(
                user=self.user,
                transaction_type='gasto',
                amount=self.bet_amount,
                description=f"Apuesta pendiente: {self.event_name}",
                date=self.date,
                account=self.account,
                related_bet=self,
                notes=f"Apuesta {self.get_bet_type_display()}" + (f" - {self.get_sport_type_display()}" if self.sport_type else "")
            )
    
    def _update_transactions(self, old_instance):
        from apps.transactions.models import Transaction
        
        # Eliminar transacciones antiguas relacionadas
        Transaction.objects.filter(related_bet=self).delete()
        
        # Crear nuevas transacciones según el resultado actual
        self._create_transactions()
    
    def _delete_transactions(self):
        from apps.transactions.models import Transaction
        Transaction.objects.filter(related_bet=self).delete()

