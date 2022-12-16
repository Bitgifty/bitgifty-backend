from django.db import models

# Create your models here.


class GiftCard(models.Model):
    wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE)
    currency = models.CharField(max_length=255)
    amount = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=0)
    note = models.TextField(null=True, blank=True)
    fees = models.FloatField(default=0.0)
    binance_code = models.CharField(max_length=255, null=True, blank=True)
    encrypted_code = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.currency
