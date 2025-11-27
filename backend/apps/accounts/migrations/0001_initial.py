from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('account_type', models.CharField(choices=[('efectivo', 'Efectivo'), ('banco', 'Cuenta Bancaria'), ('credito', 'Tarjeta de Crédito'), ('debito', 'Tarjeta de Débito'), ('billetera', 'Billetera Digital'), ('inversion', 'Cuenta de Inversión'), ('otro', 'Otro')], max_length=20, verbose_name='Tipo')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Saldo')),
                ('currency', models.CharField(choices=[('EUR', 'Euro'), ('USD', 'Dólar'), ('MXN', 'Peso Mexicano'), ('ARS', 'Peso Argentino'), ('COP', 'Peso Colombiano'), ('CLP', 'Peso Chileno')], default='EUR', max_length=3, verbose_name='Moneda')),
                ('color', models.CharField(default='#3B82F6', max_length=7, verbose_name='Color')),
                ('icon', models.CharField(default='wallet', max_length=50, verbose_name='Icono')),
                ('include_in_total', models.BooleanField(default=True, verbose_name='Incluir en total')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activa')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Cuenta',
                'verbose_name_plural': 'Cuentas',
                'ordering': ['-created_at'],
            },
        ),
    ]





