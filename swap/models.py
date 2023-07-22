import os
import requests

from django.db import models

from core.utils import Blockchain

from wallets.models import Wallet

# Create your models here.

class SwapTable(models.Model):
    buy = models.CharField(max_length=255)
    using = models.CharField(max_length=255)
    factor = models.FloatField(default=1.0)
    profit = models.FloatField(default=0.0)

    def update_factor(self):
        url = "https://api.coingecko.com/api/v3/simple/price"
        buy = self.buy
        using = self.using
        
        if buy == "naira":
            buy = "NGN"

        if using == "naira":
            using = "NGN"
        params = {
            "ids": buy.lower(),
            "vs_currencies": using.lower()
        }
        r = requests.get(url, params=params)
        data = r.json()
        return data[buy.lower()][using.lower()]
        # return data[using.lower()][buy.lower()]
    
    def save(self, *args, **kwargs):
        factor = self.update_factor()
        print(factor)
        self.factor = factor + self.profit
        return super(SwapTable, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.using} > {self.buy}"
    
    

class Swap(models.Model):
    swap_from = models.ForeignKey(Wallet, on_delete=models.SET_NULL, related_name="swap_from", null=True)
    swap_from_amount = models.FloatField(default=0.0)
    swap_to = models.ForeignKey(Wallet, on_delete=models.SET_NULL, related_name="swap_to", null=True)
    swap_table = models.OneToOneField(SwapTable, on_delete=models.SET_NULL, null=True)

    def swap_currency(self):
        TATUM_API_KEY = os.getenv("TATUM_API_KEY")
        client = Blockchain(TATUM_API_KEY)
        print(self.swap_table.factor)
        return client.initiate_swap(
            swap_to=self.swap_to, swap_amount=float(self.swap_from_amount) * float(self.swap_table.factor),
            swap_from=self.swap_from
        )

    def save(self, *args, **kwargs):
        self.swap_currency()
        return super(Swap, self).save(*args, **kwargs)
