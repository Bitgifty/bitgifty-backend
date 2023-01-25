from django.db import models

# Create your models here.


class Wallet(models.Model):
    network_choice = (
        ('Bitcoin', 'Bitcoin'), ('Ethereum', 'Ethereum'),
        ('BNB', 'BNB'), ('CELO', 'CELO'),
        ('Tron', 'Tron')
    )
    owner = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    address = models.CharField(max_length=555, null=True, blank=True)
    private_key = models.CharField(max_length=555, null=True, blank=True)
    xpub = models.CharField(max_length=555, null=True, blank=True)
    mnemonic = models.CharField(max_length=555, null=True, blank=True)
    network = models.CharField(
        max_length=555, choices=network_choice,
        null=True, blank=True
    )
    qrcode = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.owner.email

    class Meta:
        unique_together = ('owner', 'network')
