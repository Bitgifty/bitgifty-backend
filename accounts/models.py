import requests

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

import os

from core.utils import Blockchain
# Create your models here.


class Account(AbstractUser):
    wallet_address = models.TextField(max_length=255, null=True, blank=True)
    wallet_seed = models.TextField(max_length=255, null=True, blank=True)
    xpub = models.TextField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255)
    referral_code = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.email

@receiver(post_save, sender=Account)
def update_account(sender, instance, **kwargs):
    if not instance.wallet_address:
        TATUM_API_KEY = os.getenv("TATUM_API_KEY")
        client = Blockchain(key=TATUM_API_KEY)
        credentials = client.generate_credentials("tron")
        
        wallet = client.generate_wallet(credentials["xpub"], "tron")

        encrypted_credentials = client.encrypt_credentials(
            wallet["address"], credentials["mnemonic"],
            credentials["xpub"]
        )
       
        instance.xpub, instance.wallet_seed = encrypted_credentials["Xpub"], encrypted_credentials["Mnemonic"]
        instance.wallet_address = wallet["address"]
        return instance.save()
