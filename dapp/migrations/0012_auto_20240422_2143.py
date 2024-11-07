# Generated by Django 3.2 on 2024-04-22 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dapp', '0011_alter_transaction_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashback',
            name='transaction_hash',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='reward',
            name='transaction_hash',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='cashback',
            name='wallet',
            field=models.CharField(max_length=255),
        ),
    ]
