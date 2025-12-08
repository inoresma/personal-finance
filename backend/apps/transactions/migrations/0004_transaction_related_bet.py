from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0003_purchaseitem'),
        ('bets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='related_bet',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='transactions',
                to='bets.bet',
                verbose_name='Apuesta relacionada'
            ),
        ),
    ]






