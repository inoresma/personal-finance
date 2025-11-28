from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='is_ant_expense',
            field=models.BooleanField(default=False, verbose_name='Gasto hormiga'),
        ),
    ]






