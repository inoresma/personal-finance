import logging
from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.transactions.models import Transaction, PurchaseItem
from apps.categories.models import Category

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verifica y corrige referencias huérfanas de categorías en transacciones'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Corrige las referencias huérfanas estableciendo category=None',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra las referencias huérfanas sin corregirlas',
        )
    
    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        fix = options.get('fix', False)
        
        if not fix and not dry_run:
            self.stdout.write(self.style.WARNING('Usa --dry-run para ver las referencias huérfanas o --fix para corregirlas'))
            return
        
        self.stdout.write('Verificando referencias huérfanas de categorías...')
        
        orphan_transactions = []
        orphan_purchase_items = []
        
        transactions = Transaction.objects.filter(category__isnull=False).select_related('category', 'user')
        for transaction in transactions:
            category = transaction.category
            if category:
                if not Category.objects.filter(
                    Q(id=category.id),
                    Q(user=transaction.user) | Q(is_default=True, user__isnull=True)
                ).exists():
                    orphan_transactions.append({
                        'id': transaction.id,
                        'user_id': transaction.user_id,
                        'category_id': category.id,
                        'category_name': category.name,
                        'date': transaction.date,
                        'description': transaction.description
                    })
        
        purchase_items = PurchaseItem.objects.filter(category__isnull=False).select_related('category', 'transaction', 'transaction__user')
        for item in purchase_items:
            category = item.category
            if category:
                user = item.transaction.user
                if not Category.objects.filter(
                    Q(id=category.id),
                    Q(user=user) | Q(is_default=True, user__isnull=True)
                ).exists():
                    orphan_purchase_items.append({
                        'id': item.id,
                        'transaction_id': item.transaction_id,
                        'user_id': user.id,
                        'category_id': category.id,
                        'category_name': category.name,
                        'name': item.name
                    })
        
        total_orphans = len(orphan_transactions) + len(orphan_purchase_items)
        
        if total_orphans == 0:
            self.stdout.write(self.style.SUCCESS('No se encontraron referencias huérfanas'))
            return
        
        self.stdout.write(self.style.WARNING(f'Se encontraron {total_orphans} referencias huérfanas:'))
        self.stdout.write(f'  - Transacciones: {len(orphan_transactions)}')
        self.stdout.write(f'  - PurchaseItems: {len(orphan_purchase_items)}')
        
        if orphan_transactions:
            self.stdout.write('\nTransacciones con categorías huérfanas:')
            for trans in orphan_transactions[:10]:
                self.stdout.write(f'  - ID {trans["id"]}: Usuario {trans["user_id"]}, Categoría {trans["category_id"]} ({trans["category_name"]}), Fecha: {trans["date"]}')
            if len(orphan_transactions) > 10:
                self.stdout.write(f'  ... y {len(orphan_transactions) - 10} más')
        
        if orphan_purchase_items:
            self.stdout.write('\nPurchaseItems con categorías huérfanas:')
            for item in orphan_purchase_items[:10]:
                self.stdout.write(f'  - ID {item["id"]}: Transacción {item["transaction_id"]}, Usuario {item["user_id"]}, Categoría {item["category_id"]} ({item["category_name"]})')
            if len(orphan_purchase_items) > 10:
                self.stdout.write(f'  ... y {len(orphan_purchase_items) - 10} más')
        
        if fix and not dry_run:
            self.stdout.write('\nCorrigiendo referencias huérfanas...')
            
            fixed_transactions = 0
            for trans_data in orphan_transactions:
                try:
                    transaction = Transaction.objects.get(id=trans_data['id'])
                    logger.info(f'Fixing orphan category in transaction {transaction.id}: category_id={trans_data["category_id"]}')
                    transaction.category = None
                    transaction.save()
                    fixed_transactions += 1
                except Transaction.DoesNotExist:
                    logger.warning(f'Transaction {trans_data["id"]} not found')
            
            fixed_items = 0
            for item_data in orphan_purchase_items:
                try:
                    item = PurchaseItem.objects.get(id=item_data['id'])
                    logger.info(f'Fixing orphan category in PurchaseItem {item.id}: category_id={item_data["category_id"]}')
                    item.category = None
                    item.save()
                    fixed_items += 1
                except PurchaseItem.DoesNotExist:
                    logger.warning(f'PurchaseItem {item_data["id"]} not found')
            
            self.stdout.write(self.style.SUCCESS(
                f'Corregidas {fixed_transactions} transacciones y {fixed_items} purchase items'
            ))
        elif dry_run:
            self.stdout.write(self.style.WARNING('\nModo dry-run: No se realizaron cambios. Usa --fix para corregir.'))

