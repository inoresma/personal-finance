from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Debt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nombre/Descripción')),
                ('debt_type', models.CharField(choices=[('deuda', 'Deuda (Debo)'), ('prestamo', 'Préstamo (Me deben)')], max_length=10, verbose_name='Tipo')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Monto total')),
                ('paid_amount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Monto pagado')),
                ('interest_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Tasa de interés (%)')),
                ('start_date', models.DateField(verbose_name='Fecha inicio')),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='Fecha vencimiento')),
                ('creditor_debtor', models.CharField(blank=True, max_length=200, verbose_name='Acreedor/Deudor')),
                ('notes', models.TextField(blank=True, verbose_name='Notas')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Pagada')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='debts', to='accounts.account', verbose_name='Cuenta asociada')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Deuda',
                'verbose_name_plural': 'Deudas',
                'ordering': ['due_date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DebtPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Monto')),
                ('payment_date', models.DateField(verbose_name='Fecha de pago')),
                ('notes', models.CharField(blank=True, max_length=255, verbose_name='Notas')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('debt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='debts.debt')),
            ],
            options={
                'verbose_name': 'Pago de Deuda',
                'verbose_name_plural': 'Pagos de Deudas',
                'ordering': ['-payment_date'],
            },
        ),
    ]









