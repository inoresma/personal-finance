import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.categories.models import Category
from apps.accounts.models import Account
from apps.transactions.models import Transaction
from datetime import date, timedelta
from decimal import Decimal
import random

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba'
    
    def handle(self, *args, **options):
        self.stdout.write('Creando categorías predeterminadas...')
        self.create_default_categories()
        
        self.stdout.write('Creando usuario demo...')
        user = self.create_demo_user()
        
        self.stdout.write('Creando cuentas de ejemplo...')
        accounts = self.create_demo_accounts(user)
        
        self.stdout.write('Creando transacciones de ejemplo...')
        self.create_demo_transactions(user, accounts)
        
        self.stdout.write(self.style.SUCCESS('Datos de prueba creados exitosamente!'))
        self.stdout.write(self.style.SUCCESS('Usuario demo: demo@finanzas.com / demo1234'))
    
    def create_default_categories(self):
        logger.info('Creating default categories (preserving existing ones)...')
        
        existing_default_categories = Category.objects.filter(is_default=True, user__isnull=True)
        existing_default_count = existing_default_categories.count()
        logger.info(f'Found {existing_default_count} existing default categories')
        
        if existing_default_count > 0:
            logger.info(f'Existing default category IDs: {list(existing_default_categories.values_list("id", "name"))}')
        
        alimentacion, created = Category.objects.get_or_create(
            name='Alimentación',
            category_type='gasto',
            is_default=True,
            user=None,
            defaults={
                'color': '#EF4444',
                'icon': 'shopping-cart'
            }
        )
        if created:
            logger.info(f'Created default category: Alimentación (id={alimentacion.id})')
        else:
            logger.info(f'Using existing default category: Alimentación (id={alimentacion.id})')
            
            transactions_count = Transaction.objects.filter(category=alimentacion).count()
            logger.info(f'Category "Alimentación" (id={alimentacion.id}) is referenced by {transactions_count} transactions')
        
        subcats = [
            {'name': 'Supermercado', 'color': '#EF4444', 'icon': 'shopping-cart'},
            {'name': 'Restaurantes', 'color': '#F97316', 'icon': 'cake'},
            {'name': 'Delivery', 'color': '#FB923C', 'icon': 'truck'},
        ]
        for sub in subcats:
            subcat, created = Category.objects.get_or_create(
                name=sub['name'],
                category_type='gasto',
                parent=alimentacion,
                is_default=True,
                user=None,
                defaults={
                    'color': sub['color'],
                    'icon': sub['icon']
                }
            )
            if created:
                logger.info(f'Created default subcategory: {sub["name"]} (id={subcat.id})')
            else:
                logger.debug(f'Using existing default subcategory: {sub["name"]} (id={subcat.id})')
        
        otros_ingresos, created = Category.objects.get_or_create(
            name='Otros ingresos',
            category_type='ingreso',
            is_default=True,
            user=None,
            defaults={
                'color': '#6B7280',
                'icon': 'plus-circle'
            }
        )
        if created:
            logger.info(f'Created default category: Otros ingresos (id={otros_ingresos.id})')
        else:
            logger.info(f'Using existing default category: Otros ingresos (id={otros_ingresos.id})')
        
        final_count = Category.objects.filter(is_default=True, user__isnull=True).count()
        logger.info(f'Total default categories after seed: {final_count}')
    
    def create_demo_user(self):
        user, created = User.objects.get_or_create(
            email='demo@finanzas.com',
            defaults={
                'username': 'demo',
                'first_name': 'Usuario',
                'last_name': 'Demo'
            }
        )
        if created:
            user.set_password('demo1234')
            user.save()
        return user
    
    def create_demo_accounts(self, user):
        accounts_data = [
            {
                'name': 'Efectivo',
                'account_type': 'efectivo',
                'balance': Decimal('150000'),
                'currency': 'CLP',
                'color': '#22C55E',
                'icon': 'cash'
            },
            {
                'name': 'Banco Principal',
                'account_type': 'banco',
                'balance': Decimal('2500000'),
                'currency': 'CLP',
                'color': '#3B82F6',
                'icon': 'library'
            },
            {
                'name': 'Tarjeta de Crédito',
                'account_type': 'credito',
                'balance': Decimal('-320000'),
                'currency': 'CLP',
                'color': '#EF4444',
                'icon': 'credit-card'
            },
            {
                'name': 'Cuenta Ahorro USD',
                'account_type': 'banco',
                'balance': Decimal('500'),
                'currency': 'USD',
                'color': '#6366F1',
                'icon': 'globe'
            },
        ]
        
        accounts = []
        for acc_data in accounts_data:
            account, _ = Account.objects.get_or_create(
                user=user,
                name=acc_data['name'],
                defaults=acc_data
            )
            accounts.append(account)
        
        return accounts
    
    def create_demo_transactions(self, user, accounts):
        expense_cats = list(Category.objects.filter(category_type='gasto', is_default=True, parent__isnull=True))
        income_cats = list(Category.objects.filter(category_type='ingreso', is_default=True))
        
        logger.info(f'Found {len(expense_cats)} expense categories and {len(income_cats)} income categories for demo transactions')
        if expense_cats:
            logger.debug(f'Expense categories: {[c.name for c in expense_cats]}')
        if income_cats:
            logger.debug(f'Income categories: {[c.name for c in income_cats]}')
        
        today = date.today()
        
        for i in range(3):
            month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
            
            try:
                salary_category = Category.objects.get(name='Salario', is_default=True, user__isnull=True)
                logger.debug(f'Using salary category: {salary_category.name} (id={salary_category.id})')
                Transaction.objects.get_or_create(
                    user=user,
                    description=f'Salario mes {month_start.month}',
                    transaction_type='ingreso',
                    defaults={
                        'amount': Decimal('1800000'),
                        'date': month_start + timedelta(days=random.randint(0, 5)),
                        'account': accounts[1],
                        'category': salary_category
                    }
                )
            except Category.DoesNotExist:
                logger.warning(f'Category "Salario" not found, skipping salary transaction for month {month_start.month}')
            except Category.MultipleObjectsReturned:
                salary_category = Category.objects.filter(name='Salario', is_default=True, user__isnull=True).first()
                logger.warning(f'Multiple "Salario" categories found, using first one (id={salary_category.id})')
                Transaction.objects.get_or_create(
                    user=user,
                    description=f'Salario mes {month_start.month}',
                    transaction_type='ingreso',
                    defaults={
                        'amount': Decimal('1800000'),
                        'date': month_start + timedelta(days=random.randint(0, 5)),
                        'account': accounts[1],
                        'category': salary_category
                    }
                )
        
        expense_descriptions = [
            ('Alimentación', ['Compra supermercado', 'Mercado semanal', 'Frutas y verduras']),
            ('Transporte', ['Bencina', 'Metro/Bus', 'Uber']),
            ('Servicios', ['Electricidad', 'Agua', 'Internet', 'Gas']),
            ('Entretenimiento', ['Netflix', 'Cine', 'Concierto']),
            ('Restaurantes', ['Cena con amigos', 'Almuerzo trabajo', 'Café']),
            ('Salud', ['Farmacia', 'Consulta médica']),
            ('Tecnología', ['Accesorios', 'Apps']),
        ]
        
        ant_expenses = [
            ('Café de la mañana', 2500),
            ('Snack', 1500),
            ('Bebida', 1200),
            ('Galletas', 800),
            ('Propina', 500),
            ('Chicles', 600),
        ]
        
        for i in range(60):
            days_ago = random.randint(0, 90)
            trans_date = today - timedelta(days=days_ago)
            
            cat_name, descriptions = random.choice(expense_descriptions)
            category = next((c for c in expense_cats if c.name == cat_name and c.is_default and c.user is None), None)
            if not category:
                category = random.choice(expense_cats)
            description = random.choice(descriptions)
            
            amount = Decimal(str(random.randint(3000, 85000)))
            
            Transaction.objects.create(
                user=user,
                transaction_type='gasto',
                amount=amount,
                description=description,
                date=trans_date,
                account=random.choice(accounts[:2]),
                category=category,
                is_ant_expense=False
            )
        
        for i in range(25):
            days_ago = random.randint(0, 60)
            trans_date = today - timedelta(days=days_ago)
            description, amount = random.choice(ant_expenses)
            category = next((c for c in expense_cats if c.name == 'Alimentación' and c.is_default and c.user is None), None)
            if not category:
                category = expense_cats[0] if expense_cats else None
                logger.warning(f'Default "Alimentación" category not found, using first available category')
            if not category:
                logger.error('No expense categories available for ant expenses')
                continue
            
            Transaction.objects.create(
                user=user,
                transaction_type='gasto',
                amount=Decimal(str(amount)),
                description=description,
                date=trans_date,
                account=accounts[0],
                category=category,
                is_ant_expense=True
            )

