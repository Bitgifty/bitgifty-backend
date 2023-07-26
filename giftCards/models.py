import os

from django.db import models
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from rest_framework.exceptions import ParseError as ValidationError
from core.utils import Blockchain
# Create your models here.



class GiftCardFee(models.Model):
    amount = models.FloatField(default=0.0)
    network = models.CharField(max_length=255)
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
    wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE, null=True)
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
        try:
            if self._state.adding:
                if self.receipent_email:
                    subject = "Gift Card from BitGifty"
                    note = "You received a gift card from a friend"
                    if self.note:
                        note = self.note
                    html_message = render_to_string(
                        'giftcardtemplate.html',
                        {   
                            'image': self.image,
                            'receipent_email': self.receipent_email,
                            'sender_email': self.wallet.owner.email,
                            'code': self.code,
                            'note': note,
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
    wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE, null=True)
    redemption_date = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        try:
            if self._state.adding:
                giftcard = GiftCard.objects.get(code=self.code)
                note = giftcard.note
                giftcard.status = "used"
                giftcard.save()

                subject = "Gift Card Redeemed"
                html_message = render_to_string(
                    'giftcard_redeem.html',
                    {
                        'receipent_email': self.wallet.owner.email,
                        'code': self.code,
                        'note': note,
                    }
                )
                    
                plain_message = strip_tags(html_message)
                mail.send_mail(
                    subject, plain_message, "BitGifty <dev@bitgifty.com>",
                    [self.wallet.owner.email], html_message=html_message
                )
        except Exception as exception:
            raise ValidationError(exception)
        return super(Redeem, self).save(*args, **kwargs)

