# Generated by Django 3.2 on 2023-07-18 23:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0004_auto_20230718_2335'),
        ('giftCards', '0009_alter_giftcardfee_network'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='giftcard',
            name='account',
        ),
        migrations.AddField(
            model_name='giftcard',
            name='wallet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='wallets.wallet'),
        ),
    ]