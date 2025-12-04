from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_transaction_is_ant_expense'),
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nombre del producto')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Precio')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Cantidad')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_items', to='categories.category', verbose_name='Categoría')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='transactions.transaction', verbose_name='Transacción')),
            ],
            options={
                'verbose_name': 'Producto de compra',
                'verbose_name_plural': 'Productos de compra',
                'ordering': ['created_at'],
            },
        ),
    ]




