# Generated by Django 3.2 on 2023-07-29 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0004_auto_20230718_2335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='network',
            field=models.CharField(blank=True, max_length=555, null=True),
        ),
    ]
