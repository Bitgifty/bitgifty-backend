# Generated by Django 3.2 on 2023-05-16 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('giftCards', '0006_giftcard_creation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='redeem',
            name='redemption_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.CreateModel(
            name='GiftCardFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0.0)),
                ('network', models.CharField(max_length=255, unique=True)),
                ('operation', models.CharField(max_length=255)),
            ],
            options={
                'unique_together': {('network', 'operation')},
            },
        ),
    ]