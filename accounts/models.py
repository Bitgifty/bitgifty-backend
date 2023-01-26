
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.utils import Blockchain, env_init
from wallets.models import Wallet
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
    if Wallet.objects.filter(owner=instance).exists():
        pass
    else:
        try:
            TATUM_API_KEY = env("TATUM_API_KEY")
            client = Blockchain(key=TATUM_API_KEY)
            
            cloud_name = env("CLOUD_NAME")
            network_mapping = {
                "bnb": "bsc",
                "bitcoin": "bitcoin",
                "celo": "celo",
                "ethereum": "ethereum",
                "tron": "tron"
            }

            for key in network_mapping:
                credentials = client.generate_credentials(network_mapping[key])
                wallet = client.generate_wallet(credentials["xpub"], network_mapping[key])
                private_key = client.generate_private_key(credentials["mnemonic"], network_mapping[key])
                encrypted_credentials = client.encrypt_credentials(
                credentials["mnemonic"], credentials["xpub"], private_key
                )
                xpub_enc = encrypted_credentials["Xpub"]
                mnemonic_enc = encrypted_credentials["Mnemonic"]
                private_enc = encrypted_credentials["private_key"]
                wallet_address = wallet["address"]
                client.upload_qrcode(wallet_address, instance.email)

                user_wallet = Wallet(
                    owner=instance,
                    address=wallet_address,
                    private_key=private_enc.decode(),
                    xpub=xpub_enc.decode(),
                    mnemonic=mnemonic_enc.decode(),
                    network=key.title(),
                    qrcode=f'https://res.cloudinary.com/{cloud_name}/image/upload/qr_code/{instance.email}/{wallet_address}.png'
                )
                user_wallet.save()
            
        except Exception as exception:
            raise ValueError(exception)
        return instance.save()
