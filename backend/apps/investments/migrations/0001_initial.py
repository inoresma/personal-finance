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
            name='Investment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nombre')),
                ('investment_type', models.CharField(choices=[('acciones', 'Acciones'), ('fondos', 'Fondos de Inversión'), ('bonos', 'Bonos'), ('cripto', 'Criptomonedas'), ('inmuebles', 'Bienes Raíces'), ('deposito', 'Depósito a Plazo'), ('otro', 'Otro')], max_length=20, verbose_name='Tipo')),
                ('initial_amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Monto inicial')),
                ('current_amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Monto actual')),
                ('start_date', models.DateField(verbose_name='Fecha inicio')),
                ('expected_return', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Rentabilidad esperada (%)')),
                ('notes', models.TextField(blank=True, verbose_name='Notas')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activa')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='investments', to='accounts.account', verbose_name='Cuenta asociada')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Inversión',
                'verbose_name_plural': 'Inversiones',
                'ordering': ['-created_at'],
            },
        ),
    ]









