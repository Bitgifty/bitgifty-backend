from django.db import models
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Create your models here.


class Transaction(models.Model):
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)
    currency = models.CharField(max_length=255, default="naira")
    currency_type = models.CharField(max_length=255, default="fiat")
    status = models.CharField(max_length=255, default='pending')
    time = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        if self.status == "confirmed" and self.currency_type == "fiat":
            subject = "Withdrawal request processed"
            message = f"""
            Your request to withdraw the sum of {self.amount}
            has been processed successfully.
            """
            html_message = render_to_string(
            'giftcardtemplate.html',
                {
                    'receipent_email': self.user.email,
                    'amount': self.amount,
                    'currency': self.currency,
                }
            )
            plain_message = strip_tags(html_message)
            mail.send_mail(
                subject, plain_message, "BitGifty <info@bitgifty.com>",
                [self.user.email], html_message=html_message
            )
        
        return super(Transaction, self).save(*args, **kwargs)
