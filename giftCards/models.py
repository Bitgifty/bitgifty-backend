import environ
import os

from django.db import models
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.exceptions import ValidationError
from core.utils import Blockchain
from wallets.models import Wallet
# Create your models here.

env = environ.Env()
# reading .env file
environ.Env.read_env()


class GiftCardFee(models.Model):
    amount = models.FloatField(default=0.0)
    network = models.CharField(unique=True, max_length=255)
    operation = models.CharField(max_length=255)

    def __str__(self):
        return self.network

    class Meta:
        unique_together = ("network", "operation")


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
    receipent_email = models.EmailField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    fees = models.FloatField(default=0.0)
    code = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default="generated")
    creation_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.currency

    def save(self, *args, **kwargs):
        TATUM_API_KEY = os.getenv("TATUM_API_KEY")
        client = Blockchain(TATUM_API_KEY, os.getenv("BIN_KEY"), os.getenv("BIN_SECRET"))
        try:
            if self._state.adding:
                try:
                    fee = GiftCardFee.objects.get(network=self.currency.title(), operation="create").amount
                except Exception:
                    fee = 0.0
                wallet = Wallet.objects.get(owner=self.account, network=self.currency.title())
                admin_wallet = Wallet.objects.filter(owner__username="superman-houseboy", network=self.currency.title()).first()
                charge = float(self.amount + fee)
                giftcard = client.create_gift_card(
                    wallet.private_key, charge,
                    admin_wallet.address,
                    self.currency, wallet.address
                )
                self.code = giftcard
                if self.receipent_email:
                    subject = "Gift Card from BitGifty"
                    html_message = render_to_string(
                        'giftcard_mail.html',
                        {
                            'receipent_email': self.receipent_email,
                            'sender_email': self.account.email,
                            'code': self.code,
                        }
                    )
                    plain_message = strip_tags(html_message)
                    mail.send_mail(
                        subject, plain_message, "BitGifty <dev@bitgifty.com>",
                        [self.receipent_email], html_message=html_message
                    )

        except Exception as exception:
            raise ValidationError(exception)
        return super(GiftCard, self).save(*args, **kwargs)


class Redeem(models.Model):
    code = models.CharField(max_length=255)
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, null=True)
    redemption_date = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        try:
            try:
                fee = GiftCardFee.objects.get(network=self.currency.title(), operation="redeem")
            except Exception:
                fee = 0.0
            giftcard = GiftCard.objects.get(code=self.code)
            if giftcard.status == "used":
                raise ValidationError("Gift card has been used")
            TATUM_API_KEY = os.getenv("TATUM_API_KEY")
            client = Blockchain(TATUM_API_KEY, os.getenv("BIN_KEY"), os.getenv("BIN_SECRET"))
            wallet = Wallet.objects.get(owner=self.account, network=giftcard.currency.title())
            admin_wallet = Wallet.objects.get(owner__username="superman-houseboy", network=giftcard.currency.title())
            amount = str(giftcard.amount + fee.amount)
        
            client.redeem_gift_card(
                self.code, admin_wallet.private_key, amount,
                wallet.address, giftcard.currency, admin_wallet.address
            )
    
            giftcard.status = "used"
            giftcard.save()
        except Exception as exception:
            raise ValidationError(exception)
        return super(Redeem, self).save(*args, **kwargs)

