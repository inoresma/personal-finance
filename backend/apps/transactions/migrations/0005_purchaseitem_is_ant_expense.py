from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0004_transaction_related_bet'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseitem',
            name='is_ant_expense',
            field=models.BooleanField(default=False, verbose_name='Gasto hormiga'),
        ),
    ]



