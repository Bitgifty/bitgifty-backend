import os

from django.db import models

from core.utils import Blockchain

from wallets.models import Wallet

# Create your models here.

class SwapTable(models.Model):
    first_currency = models.CharField(max_length=255)
    second_currency = models.CharField(max_length=255)
    factor = models.FloatField(default=1.0)

    def __str__(self):
        return f"{self.first_currency}"
    

class Swap(models.Model):
    swap_from = models.ForeignKey(Wallet, on_delete=models.SET_NULL, related_name="swap_from", null=True)
    swap_from_amount = models.FloatField(default=0.0)
    swap_to = models.ForeignKey(Wallet, on_delete=models.SET_NULL, related_name="swap_to", null=True)
    swap_table = models.OneToOneField(SwapTable, on_delete=models.SET_NULL, null=True)

    def swap_currency(self):
        TATUM_API_KEY = os.getenv("TATUM_API_KEY")
        client = Blockchain(TATUM_API_KEY)

        return client.initiate_swap(
            self.swap_from, self.swap_from_amount*self.swap_table.factor,
            self.swap_to
        )

    def save(self, *args, **kwargs):
        self.swap_currency()
        return super(Swap, self).save(*args, **kwargs)