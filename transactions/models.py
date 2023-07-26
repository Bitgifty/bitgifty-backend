from django.db import models
from django.core import mail

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
            subject = f"Withdrawal request processed"
            message = f"""
            Your request to withdraw the sum of {self.amount}
            has been processed successfully.
            """
            mail.send_mail(
                subject, message, "info@bitgifty.com",
                [self.user.email,]
            )
        
        return super(Transaction, self).save(*args, **kwargs)
