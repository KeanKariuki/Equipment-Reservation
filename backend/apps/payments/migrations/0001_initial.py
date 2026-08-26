import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reservations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=100, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, help_text='KES. Matches reservation.total_amount at the time of initialization.', max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('paystack_transaction_id', models.CharField(blank=True, max_length=100)),
                ('channel', models.CharField(blank=True, help_text='How they paid, e.g. card, mobile_money, bank_transfer.', max_length=50)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('raw_response', models.JSONField(blank=True, help_text='Last Paystack response for this payment, kept for support/debugging.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reservation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='reservations.reservation')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
