import requests

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from cryptography.fernet import Fernet
# Create your models here.


class Account(AbstractUser):
    wallet_address = models.CharField(max_length=255, null=True, blank=True)
    wallet_seed = models.CharField(max_length=255, null=True, blank=True)
    xpub = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=255)
    referral_code = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.email

def encrypt_data(address: str, mnemonic: str, xpub: str):
    key = f"{address}787898"

    fernet = Fernet(key)

    encMnemonic = fernet.encrypt(mnemonic.encode())
    encXpub = fernet.encrypt(xpub.encode())

    return encMnemonic, encXpub

@receiver(post_save, Account)
def update_account(sender, instance, **kwargs):
    if instance.wallet_address and not instance.wallet_seed:
        url = "https://api.tatum.io/v3/ethereum/wallet"
        headers = {"x-api-key": "YOUR_API_KEY_HERE"}
        response = requests.get(url, headers=headers)
        data = response.json()
        mnemonic = data.mnemonic
        xpub = data.xpub
        instance.xpub, instance.wallet_seed = encrypt_data(
            instance.wallet_address,
            mnemonic, xpub
        )
        return instance.save()
