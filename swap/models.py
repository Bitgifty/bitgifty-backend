import os
import requests

from django.db import models

from core.utils import Blockchain, get_rate, get_naira_price

from wallets.models import Wallet

# Create your models here.


class USDTNaira(models.Model):
    price = models.FloatField(default=0.0)

    def __str__(self) -> str:
        return "usdt > naira"


class USDTPrice(models.Model):
    coin = models.CharField(max_length=255, null=True)
    price = models.FloatField(default=0.0)

    def __str__(self) -> str:
        return f"{self.coin} > naira"

    def get_rate(self, coin):
        request = requests.get(f"https://api.binance.com/api/v3/avgPrice?symbol={coin}USDT")
        data = request.json()
        try:
            price = data["price"]
            return price
        except KeyError:
            raise ValueError("Price not found")

    def save(self, *args, **kwargs):
        coin = {
            "tron": "TRX",
            "bnb": "BNB",
            "bitcoin": "BTC",
            "celo": "CELO",
            "ethereum": "ETH"
        }
        self.price = self.get_rate(coin[self.coin.lower()])
        return super(USDTPrice, self).save(*args, **kwargs)

class SwapTable(models.Model):
    buy = models.CharField(max_length=255)
    using = models.CharField(max_length=255)
    naira_factor = models.ForeignKey(USDTNaira, on_delete=models.CASCADE, null=True)
    usd_price = models.ForeignKey(USDTPrice, on_delete=models.CASCADE, null=True)
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
            "ids": using.lower(),
            "vs_currencies": "ngn"
        }
        r = requests.get(url, params=params)
        data = r.json()
        try:
            return data[using.lower()]["ngn"]
        except KeyError:
            return self.factor

    def __str__(self):
        return f"{self.using} > {self.buy}"
    
    

class Swap(models.Model):
    swap_from = models.ForeignKey(Wallet, on_delete=models.SET_NULL, related_name="swap_from", null=True)
    swap_amount = models.FloatField(default=0.0)
    swap_to = models.ForeignKey(Wallet, on_delete=models.SET_NULL, related_name="swap_to", null=True)
    swap_table = models.ForeignKey(SwapTable, on_delete=models.SET_NULL, null=True)
    swap_date = models.DateTimeField(auto_now_add=True, null=True)

    def swap_currency(self):
        TATUM_API_KEY = os.getenv("TATUM_API_KEY")
        client = Blockchain(TATUM_API_KEY)
        usdt_price = get_rate(self.swap_table.using)
        naira_price = get_naira_price()
        return client.initiate_swap(
            swap_to=self.swap_to, swap_amount=float(self.swap_amount), factor=naira_price,
            swap_from=self.swap_from, usdt_price=usdt_price
        )

    def save(self, *args, **kwargs):
        self.swap_currency()
        return super(Swap, self).save(*args, **kwargs)
