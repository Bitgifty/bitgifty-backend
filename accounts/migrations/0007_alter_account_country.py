# Generated by Django 3.2 on 2023-05-29 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20230120_0823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='country',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
