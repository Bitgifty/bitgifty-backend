# Generated by Django 3.2 on 2023-01-19 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20230114_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='private_key',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
    ]
