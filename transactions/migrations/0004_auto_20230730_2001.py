# Generated by Django 3.2 on 2023-07-30 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0003_auto_20230726_0716'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='account_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='bank_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
