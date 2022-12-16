from django.db import models

# Create your models here.


class Wallet(models.Model):
    owner = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    balance = models.FloatField(default=0.0)

    def __str__(self):
        return self.owner.email

    def fund(self, amount):
        self.balance += amount
        self.save()
    
    def debit(self, amount):
        self.balance -= amount
        self.save()
