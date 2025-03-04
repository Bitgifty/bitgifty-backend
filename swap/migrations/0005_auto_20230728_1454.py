# Generated by Django 3.2 on 2023-07-28 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('swap', '0004_alter_swap_swap_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='USDTNaira',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='USDTPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(default=0.0)),
            ],
        ),
        migrations.RemoveField(
            model_name='swaptable',
            name='factor',
        ),
        migrations.AddField(
            model_name='swaptable',
            name='naira_factor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='swap.usdtnaira'),
        ),
        migrations.AddField(
            model_name='swaptable',
            name='usd_price',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='swap.usdtprice'),
        ),
    ]
