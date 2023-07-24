from django.db import models

# Create your models here.


class Payout(models.Model):
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)

    def __str__(self):
        return self.account_name

