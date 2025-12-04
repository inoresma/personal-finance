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
            name='Bet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bet_type', models.CharField(choices=[('deportes', 'Deportes'), ('blackjack', 'Blackjack'), ('poker', 'Poker'), ('ruleta', 'Ruleta'), ('tragamonedas', 'Tragamonedas'), ('otros', 'Otros')], max_length=20, verbose_name='Tipo de apuesta')),
                ('event_name', models.CharField(max_length=255, verbose_name='Evento/Descripción')),
                ('sport_type', models.CharField(blank=True, choices=[('futbol', 'Fútbol'), ('basquet', 'Básquetbol'), ('tenis', 'Tenis'), ('beisbol', 'Béisbol'), ('futbol_americano', 'Fútbol Americano'), ('hockey', 'Hockey'), ('boxeo', 'Boxeo'), ('mma', 'MMA'), ('otros', 'Otros')], max_length=20, null=True, verbose_name='Tipo de deporte')),
                ('bet_amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Monto apostado')),
                ('odds', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cuota/Odds')),
                ('result', models.CharField(choices=[('ganó', 'Ganó'), ('perdió', 'Perdió'), ('pendiente', 'Pendiente')], default='pendiente', max_length=10, verbose_name='Resultado')),
                ('payout_amount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Monto ganado')),
                ('date', models.DateField(verbose_name='Fecha')),
                ('notes', models.TextField(blank=True, verbose_name='Notas')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bets', to='accounts.account', verbose_name='Cuenta')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Apuesta',
                'verbose_name_plural': 'Apuestas',
                'ordering': ['-date', '-created_at'],
            },
        ),
    ]



