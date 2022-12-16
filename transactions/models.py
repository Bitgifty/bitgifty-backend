from django.db import models

# Create your models here.


class Transaction(models.Model):
    wallet = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)
    asset = models.CharField(max_length=255)
    action = models.CharField(max_length=255)

    def __str__(self):
        return self.wallet.email
