# Generated by Django 3.2 on 2024-06-08 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dapp', '0012_auto_20240422_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='country',
            field=models.CharField(blank=True, default='NG', max_length=255, null=True),
        ),
    ]
