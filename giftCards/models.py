import environ

from django.db import models
from rest_framework.exceptions import ValidationError
from core.utils import Blockchain
from wallets.models import Wallet
# Create your models here.

env = environ.Env()
# reading .env file
environ.Env.read_env()

class GiftCardImage(models.Model):
    link = models.URLField(null=True)
    
    def __str__(self):
        return str(self.link)

class GiftCard(models.Model):
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, null=True)
    currency = models.CharField(max_length=255)
    amount = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=0)
    image = models.ForeignKey(GiftCardImage, on_delete=models.SET_NULL, null=True)
    note = models.TextField(null=True, blank=True)
    fees = models.FloatField(default=0.0)
    code = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default="generated")

    def __str__(self):
        return self.currency

    def save(self, *args, **kwargs):
        TATUM_API_KEY = env("TATUM_API_KEY")
        client = Blockchain(TATUM_API_KEY, env("BIN_KEY"), env("BIN_SECRET"))
        try:
            if self._state.adding:
                wallet = Wallet.objects.get(owner=self.account, network=self.currency.title())
                admin_wallet = Wallet.objects.filter(owner__username="superman-houseboy", network=self.currency.title()).first()
                charge = self.amount
                giftcard = client.create_gift_card(
                    wallet.private_key, charge,
                    admin_wallet.address,
                    self.currency, wallet.address
                )
                self.code = giftcard
        except Exception as exception:
            raise ValidationError(exception)
        return super(GiftCard, self).save(*args, **kwargs)


class Redeem(models.Model):
    code = models.CharField(max_length=255)
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        try:
            giftcard = GiftCard.objects.get(code=self.code)
            if giftcard.status == "used":
                raise ValidationError("Gift card has been used")
            TATUM_API_KEY = env("TATUM_API_KEY")
            client = Blockchain(TATUM_API_KEY, env("BIN_KEY"), env("BIN_SECRET"))
            wallet = Wallet.objects.get(owner=self.account, network=giftcard.currency.title())
            admin_wallet = Wallet.objects.get(owner__username="superman-houseboy", network=giftcard.currency.title())
            amount = str(giftcard.amount)
        
            client.redeem_gift_card(
                self.code, admin_wallet.private_key, amount,
                wallet.address, giftcard.currency, admin_wallet.address
            )
    
            giftcard.status = "used"
            giftcard.save()
        except Exception as exception:
            raise ValidationError(exception)
        return super(Redeem, self).save(*args, **kwargs)
