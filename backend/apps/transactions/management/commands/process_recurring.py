from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.transactions.models import Transaction, RecurringTransaction


class Command(BaseCommand):
    help = 'Procesa las transacciones recurrentes pendientes'
    
    def handle(self, *args, **options):
        today = timezone.now().date()
        
        recurring = RecurringTransaction.objects.filter(
            is_active=True,
            next_execution__lte=today
        ).select_related('account', 'destination_account', 'category', 'user')
        
        processed = 0
        
        for rec in recurring:
            if rec.end_date and rec.end_date < today:
                rec.is_active = False
                rec.save()
                continue
            
            Transaction.objects.create(
                user=rec.user,
                transaction_type=rec.transaction_type,
                amount=rec.amount,
                description=rec.description,
                date=rec.next_execution,
                account=rec.account,
                destination_account=rec.destination_account,
                category=rec.category,
                is_recurring=True
            )
            
            rec.last_executed = rec.next_execution
            rec.next_execution = self.calculate_next_date(rec.next_execution, rec.frequency)
            rec.save()
            
            processed += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Procesadas {processed} transacciones recurrentes')
        )
    
    def calculate_next_date(self, current_date, frequency):
        if frequency == 'diaria':
            return current_date + timedelta(days=1)
        elif frequency == 'semanal':
            return current_date + timedelta(weeks=1)
        elif frequency == 'quincenal':
            return current_date + timedelta(days=15)
        elif frequency == 'mensual':
            month = current_date.month + 1
            year = current_date.year
            if month > 12:
                month = 1
                year += 1
            day = min(current_date.day, 28)
            return current_date.replace(year=year, month=month, day=day)
        elif frequency == 'anual':
            return current_date.replace(year=current_date.year + 1)
        return current_date









