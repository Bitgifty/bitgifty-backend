import os

from django.db import models

from core.utils import Blockchain
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
    status = models.CharField(max_length=255, default="generated")

    def __str__(self):
        return self.currency

    def save(self, *args, **kwargs):
        TATUM_API_KEY = os.getenv("TATUM_API_KEY")
        client = Blockchain(key=TATUM_API_KEY)
        giftcard = client.create_gift_card(self.currency, str(self.amount))
        self.binance_code = giftcard["code"]
        return super(self, GiftCard).save(*args, **kwargs)


class Redeem(models.Model):
    code = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        TATUM_API_KEY = os.getenv("TATUM_API_KEY")
        client = Blockchain(key=TATUM_API_KEY)
        giftcard = client.reedem_gift_card(self.code)
        self.binance_code = giftcard["code"]
        return super(self, GiftCard).save(*args, **kwargs)
