# Generated by Django 3.2 on 2023-07-19 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swap', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='swaptable',
            old_name='first_currency',
            new_name='buy',
        ),
        migrations.RenameField(
            model_name='swaptable',
            old_name='second_currency',
            new_name='using',
        ),
        migrations.AddField(
            model_name='swaptable',
            name='profit',
            field=models.FloatField(default=0.0),
        ),
    ]
