import os

from django.db import models
from django.core.exceptions import ValidationError

from core.utils import Blockchain
# Create your models here.


class GiftCard(models.Model):
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, null=True)
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
        client = Blockchain(TATUM_API_KEY, os.getenv("BIN_KEY"), os.getenv("BIN_SECRET"))
        try:
            giftcard = client.create_gift_card(self.currency, str(self.amount))
            self.binance_code = giftcard["code"]
        except Exception as exception:
            raise ValidationError(exception)
        return super(self, GiftCard).save(*args, **kwargs)


class Redeem(models.Model):
    code = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        TATUM_API_KEY = os.getenv("TATUM_API_KEY")
        client = Blockchain(TATUM_API_KEY, os.getenv("BIN_KEY"), os.getenv("BIN_SECRET"))
        
        try:
            giftcard = client.reedem_gift_card(self.code)
            self.binance_code = giftcard["code"]
        except Exception as exception:
            raise ValidationError(exception)
        return super(self, Redeem).save(*args, **kwargs)
