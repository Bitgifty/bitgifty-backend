import os

from django.db import models

from core.utils import Blockchain

# Create your models here.


class DataPurchase(models.Model):
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE, null=True)
    network = models.CharField(max_length=255)
    phone = models.CharField(max_length=11)
    data_plan = models.CharField(max_length=255)
    request_id = models.CharField(max_length=255)

    def __str__(self):
        return self.user.email
    
    def purchase(self):
        client = Blockchain(key=os.getenv("TATUM_API_KEY"))
        wallet = self.wallet
        amount = client.get_data_plan(self.network, self.data_plan)
        return client.buy_data(wallet, amount, self.network, self.phone)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.purchase()
        return super(DataPurchase, self).save(*args, **kwargs)


class AirtimePurchase(models.Model):
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE, null=True)
    network = models.CharField(max_length=255)
    phone = models.CharField(max_length=11)
    plan_type = models.CharField(max_length=255)
    amount = models.IntegerField(default=0)
    request_id = models.CharField(max_length=255)

    def __str__(self):
        return self.user.email
    
    def purchase(self):
        client = Blockchain(key=os.getenv("TATUM_API_KEY"))
        wallet = self.wallet
        return client.buy_airtime(wallet, self.network, self.phone, self.amount)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.purchase()
        return super(AirtimePurchase, self).save(*args, **kwargs)


class CablePurchase(models.Model):
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE, null=True)
    iuc = models.CharField(max_length=255)
    cable_plan = models.CharField(max_length=255)
    
    def __str__(self):
        return self.user.email
    
    def purchase(self):
        client = Blockchain(key=os.getenv("TATUM_API_KEY"))
        wallet = self.wallet
        plan_id = self.cable_plan
        amount = 0
        return client.buy_cable(wallet, self.cable_plan, self.iuc, plan_id, amount)
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            self.purchase()
        return super(CablePurchase, self).save(*args, **kwargs)


class ElectricityPurchase(models.Model):
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE, null=True)
    disco = models.CharField(max_length=255)
    meter_type = models.CharField(max_length=255)
    meter_number = models.CharField(max_length=255)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email
    
    def purchase(self):
        client = Blockchain(key=os.getenv("TATUM_API_KEY"))
        wallet = self.wallet
        return client.buy_electricity(
            wallet, self.disco, self.meter_type,
            self.meter_number, self.amount
        )

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.purchase()
        return super(ElectricityPurchase, self).save(*args, **kwargs)
