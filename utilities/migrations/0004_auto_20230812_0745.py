# Generated by Django 3.2 on 2023-08-12 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0003_auto_20230812_0741'),
    ]

    operations = [
        migrations.AddField(
            model_name='cableplan',
            name='amount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cableplan',
            name='plan_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]