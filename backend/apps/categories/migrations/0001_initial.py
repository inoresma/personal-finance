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
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('category_type', models.CharField(choices=[('ingreso', 'Ingreso'), ('gasto', 'Gasto')], max_length=10, verbose_name='Tipo')),
                ('color', models.CharField(default='#6366F1', max_length=7, verbose_name='Color')),
                ('icon', models.CharField(default='tag', max_length=50, verbose_name='Icono')),
                ('is_default', models.BooleanField(default=False, verbose_name='Es predeterminada')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='categories.category', verbose_name='Categoría padre')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categories', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Categoría',
                'verbose_name_plural': 'Categorías',
                'ordering': ['category_type', 'name'],
            },
        ),
    ]







