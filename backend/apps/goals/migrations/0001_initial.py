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
            name='Goal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nombre')),
                ('goal_type', models.CharField(choices=[('savings', 'Meta de Ahorro'), ('category_reduction', 'Reducción por Categoría')], max_length=20, verbose_name='Tipo de Meta')),
                ('target_amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Monto Objetivo')),
                ('target_date', models.DateField(verbose_name='Fecha Límite')),
                ('reduction_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Porcentaje de Reducción (%)')),
                ('baseline_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Monto Base')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activa')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='goals', to='categories.category', verbose_name='Categoría')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goals', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Meta',
                'verbose_name_plural': 'Metas',
                'ordering': ['-created_at'],
            },
        ),
    ]

