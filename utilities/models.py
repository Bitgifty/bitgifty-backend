import os

from django.db import models

from django.core.exceptions import ValidationError

from core.utils import Blockchain

from wallets.models import Wallet

from core.utils import get_naira_price, get_rate

# Create your models here.


class Cable(models.Model):
    name = models.CharField(max_length=255)
    plan_id = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    

class CablePlan(models.Model):
    cable = models.ForeignKey(Cable, on_delete=models.CASCADE)
    plan_id = models.IntegerField(default=0)
    plan_name = models.CharField(max_length=255, null=True)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.cable.name}: {self.plan_name}"


class Network(models.Model):
    name = models.CharField(max_length=255)
    plan_id = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    

class DataPlan(models.Model):
    plan_id = models.IntegerField(default=0)
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=255)
    plan_name = models.CharField(max_length=255)
    amount = models.IntegerField(default=0)
    validity = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.network}: {self.plan_name}"


class Disco(models.Model):
    disco_name = models.CharField(max_length=255)
    plan_id = models.IntegerField(default=0)

    def __str__(self):
        return self.disco_name


class DataPurchase(models.Model):
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    wallet_id = models.IntegerField(default=0)
    wallet_from = models.CharField(max_length=255, default="naira")
    phone = models.CharField(max_length=11)
    data_plan = models.ForeignKey(DataPlan, on_delete=models.CASCADE)
    request_id = models.CharField(max_length=255)
    token_amount = models.FloatField(default=0.0)

    def __str__(self):
        return self.user.email
    
    def purchase(self, token_amount):
        client = Blockchain(key=os.getenv("TATUM_API_KEY"))
        wallet = Wallet.objects.get(owner=self.user, network__icontains=self.wallet_from)
        amount = self.data_plan.amount
    
        return client.buy_data(
            wallet, amount, self.data_plan.network.plan_id, self.phone,
            self.data_plan.plan_id, token_amount
        )

    def save(self, *args, **kwargs):
        if self._state.adding:
            try:
                if self.wallet_from == "naira":
                    token_amount = self.data_plan.amount
                else:
                    usd_price = get_rate(self.wallet_from.lower())
                    coin = 1/usd_price

                    naira_rate = get_naira_price()
                    naira = 1/naira_rate

                    rate = round(naira * coin, 3)

                    token_amount = self.token_amount/rate
            except Exception as ex:
                raise ValueError("Error converting naira to crypto")
            self.purchase(token_amount)
            self.token_amount = token_amount
        return super(DataPurchase, self).save(*args, **kwargs)


class AirtimePurchase(models.Model):
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    wallet_id = models.IntegerField(default=0)
    wallet_from = models.CharField(max_length=255, default="naira")
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11)
    plan_type = models.CharField(max_length=255)
    amount = models.IntegerField(default=0)
    token_amount = models.FloatField(default=0.0)
    request_id = models.CharField(max_length=255)

    def __str__(self):
        return self.user.email
    
    def purchase(self, token_amount):
        client = Blockchain(key=os.getenv("TATUM_API_KEY"))
        wallet = Wallet.objects.get(owner=self.user, network__icontains=self.wallet_from)
        
        return client.buy_airtime(
            wallet, self.network.name, self.phone, self.amount,
            token_amount
        )

    def save(self, *args, **kwargs):
        if self._state.adding:
            try:
                if self.wallet_from == "naira":
                    token_amount = self.amount
                else:
                    usd_price = get_rate(self.wallet_from.lower())
                    coin = 1/usd_price

                    naira_rate = get_naira_price()
                    naira = 1/naira_rate

                    rate = round(naira * coin, 3)

                    token_amount = self.token_amount/rate
            except Exception as exception:
                print(exception)
                raise ValueError("Error converting naira to crypto")
            self.purchase(token_amount)
            self.token_amount = token_amount
        return super(AirtimePurchase, self).save(*args, **kwargs)


class CablePurchase(models.Model):
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    wallet_id = models.IntegerField(default=0)
    wallet_from = models.CharField(max_length=255, default="naira")
    iuc = models.CharField(max_length=255)
    cable_plan = models.ForeignKey(CablePlan, on_delete=models.CASCADE)
    token_amount = models.FloatField(default=0.0)
    
    def __str__(self):
        return self.user.email
    
    def purchase(self, token_amount):
        client = Blockchain(key=os.getenv("TATUM_API_KEY"))
        wallet = Wallet.objects.get(owner=self.user, network__icontains=self.wallet_from)
        plan_id = self.cable_plan.plan_id
        
        return client.buy_cable(
            wallet, self.cable_plan.cable.plan_id, self.iuc, plan_id, token_amount
        )
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            try:
                if self.wallet_from == "naira":
                    token_amount = self.data_plan.amount
                else:
                    usd_price = get_rate(self.wallet_from.lower())
                    coin = 1/usd_price

                    naira_rate = get_naira_price()
                    naira = 1/naira_rate

                    rate = round(naira * coin, 3)

                    token_amount = self.token_amount/rate
            except Exception:
                raise ValueError("Error converting naira to crypto")
            self.purchase(token_amount)
            self.token_amount = token_amount
        return super(CablePurchase, self).save(*args, **kwargs)


class ElectricityPurchase(models.Model):
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    wallet_id = models.IntegerField(default=0)
    wallet_from = models.CharField(max_length=255, default="naira")
    disco = models.ForeignKey(Disco, on_delete=models.CASCADE)
    meter_type = models.CharField(max_length=255)
    meter_number = models.CharField(max_length=255)
    amount = models.IntegerField(default=0)
    token_amount = models.FloatField(default=0.0)

    def __str__(self):
        return self.user.email
    
    def purchase(self, token_amount):
        client = Blockchain(key=os.getenv("TATUM_API_KEY"))
        wallet = Wallet.objects.get(owner=self.user, network__icontains=self.wallet_from)
        return client.buy_electricity(
            wallet, self.disco.plan_id, self.meter_type,
            self.meter_number, self.amount, token_amount
        )

    def save(self, *args, **kwargs):
        if self._state.adding:
            try:
                if self.wallet_from == "naira":
                    token_amount = self.data_plan.amount
                else:
                    usd_price = get_rate(self.wallet_from.lower())
                    coin = 1/usd_price

                    naira_rate = get_naira_price()
                    naira = 1/naira_rate

                    rate = round(naira * coin, 3)

                    token_amount = self.token_amount/rate
            except Exception:
                raise ValueError("Error converting naira to crypto")
            self.purchase(token_amount)
            self.token_amount = token_amount
        return super(ElectricityPurchase, self).save(*args, **kwargs)
