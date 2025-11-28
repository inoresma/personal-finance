from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_limit', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Límite')),
                ('period', models.CharField(choices=[('semanal', 'Semanal'), ('mensual', 'Mensual'), ('anual', 'Anual')], default='mensual', max_length=10, verbose_name='Período')),
                ('start_date', models.DateField(verbose_name='Fecha inicio')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Fecha fin')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('alert_threshold', models.IntegerField(default=80, verbose_name='Umbral de alerta (%)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to='categories.category', verbose_name='Categoría')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Presupuesto',
                'verbose_name_plural': 'Presupuestos',
                'ordering': ['-created_at'],
            },
        ),
    ]







