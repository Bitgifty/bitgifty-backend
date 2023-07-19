# Generated by Django 3.2 on 2023-07-18 23:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0004_auto_20230718_2335'),
        ('giftCards', '0010_auto_20230718_2335'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='redeem',
            name='account',
        ),
        migrations.AddField(
            model_name='redeem',
            name='wallet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='wallets.wallet'),
        ),
    ]
