from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('ingreso', 'Ingreso'), ('gasto', 'Gasto'), ('transferencia', 'Transferencia')], max_length=15, verbose_name='Tipo')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Monto')),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='Descripción')),
                ('notes', models.TextField(blank=True, verbose_name='Notas')),
                ('date', models.DateField(verbose_name='Fecha')),
                ('is_recurring', models.BooleanField(default=False, verbose_name='Es recurrente')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='accounts.account', verbose_name='Cuenta')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='categories.category', verbose_name='Categoría')),
                ('destination_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='incoming_transfers', to='accounts.account', verbose_name='Cuenta destino')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Transacción',
                'verbose_name_plural': 'Transacciones',
                'ordering': ['-date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='RecurringTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('ingreso', 'Ingreso'), ('gasto', 'Gasto'), ('transferencia', 'Transferencia')], max_length=15, verbose_name='Tipo')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Monto')),
                ('description', models.CharField(max_length=255, verbose_name='Descripción')),
                ('frequency', models.CharField(choices=[('diaria', 'Diaria'), ('semanal', 'Semanal'), ('quincenal', 'Quincenal'), ('mensual', 'Mensual'), ('anual', 'Anual')], max_length=10, verbose_name='Frecuencia')),
                ('start_date', models.DateField(verbose_name='Fecha inicio')),
                ('next_execution', models.DateField(verbose_name='Próxima ejecución')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Fecha fin')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activa')),
                ('last_executed', models.DateField(blank=True, null=True, verbose_name='Última ejecución')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.account', verbose_name='Cuenta')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='categories.category', verbose_name='Categoría')),
                ('destination_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recurring_incoming', to='accounts.account', verbose_name='Cuenta destino')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurring_transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Transacción Recurrente',
                'verbose_name_plural': 'Transacciones Recurrentes',
                'ordering': ['next_execution'],
            },
        ),
    ]







