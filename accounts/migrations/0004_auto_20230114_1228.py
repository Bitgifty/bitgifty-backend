# Generated by Django 3.2 on 2023-01-14 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_account_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='wallet_address',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='wallet_seed',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='xpub',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
    ]
