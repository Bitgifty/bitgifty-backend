from django.db import models

# Create your models here.


class Transaction(models.Model):
    wallet = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)
    asset = models.CharField(max_length=255, default="USDT")
    action = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default='pending')
    time = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.wallet.email

    def save(self, *args, **kwargs):
        if self.status == "confirmed":
            if self.action == "deposit":
                self.wallet.amount += self.amount
                self.wallet.save()
            else:
                self.wallet.amount -= self.amount
                self.wallet.save()
        
        return super(Transaction, self).save(*args, **kwargs)
