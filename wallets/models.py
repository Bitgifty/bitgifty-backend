from django.db import models
from django.core import mail
from django.forms.formsets import ORDERING_FIELD_NAME
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
        return self.owner.email +": "+ self.network

    class Meta:
        unique_together = ('owner', 'network')


class FiatWallet(models.Model):
    owner = models.OneToOneField('accounts.Account', on_delete=models.CASCADE)
    balance = models.FloatField(default=0.0)
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.owner.email}"
    
    def get_balance(self):
        return self.balance
    
    def deposit(self, amount: float):
        self.balance += amount
        return self.balance

    def notify_withdraw_handler(self, amount):
        subject = f"Withdrawal request from {self.owner.email}"
        message = f"""{self.owner.email} has requested to withdraw the sum
        of {amount}.
        Here are the bank details:

        Bank name: {self.bank_name}
        Account name: {self.account_name}
        Account number: {self.account_number}
        """
        mail.send_mail(
            subject, message, "info@bitgifty.com",
            ["wasiuadegoke14@gmail.com", "princewillolaiya@gmail.com"]
        )
    
    def withdraw(self, amount: float):
        self.balance -= amount
        return self.balance
 
