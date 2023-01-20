
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.utils import Blockchain, env_init
# Create your models here.

env = env_init()
class Account(AbstractUser):
    private_key = models.CharField(max_length=555, null=True, blank=True)
    wallet_address = models.CharField(max_length=555, null=True, blank=True)
    wallet_seed = models.CharField(max_length=555, null=True, blank=True)
    xpub = models.CharField(max_length=555, null=True, blank=True)
    country = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255)
    referral_code = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.email

@receiver(post_save, sender=Account)
def update_account(sender, instance, **kwargs):
    if not instance.wallet_address:
        TATUM_API_KEY = env("TATUM_API_KEY")
        client = Blockchain(key=TATUM_API_KEY)
        credentials = client.generate_credentials("tron")
        
        wallet = client.generate_wallet(credentials["xpub"], "tron")
        private_key = client.generate_private_key(credentials["mnemonic"], "tron")
        encrypted_credentials = client.encrypt_credentials(
           credentials["mnemonic"], credentials["xpub"], private_key
        )
        xpub_enc = encrypted_credentials["Xpub"]
        mnemonic_enc = encrypted_credentials["Mnemonic"]
        private_enc = encrypted_credentials["private_key"]

        instance.xpub, instance.wallet_seed = xpub_enc.decode(), mnemonic_enc.decode()
        instance.wallet_address = wallet["address"]
        instance.private_key = private_enc.decode()
        return instance.save()
