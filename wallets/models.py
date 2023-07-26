import os

from django.db import models
from django.core import mail

from giftCards.models import GiftCardFee, GiftCard

from core.utils import Blockchain
from payouts.models import Payout
# Create your models here.


class Wallet(models.Model):
    network_choice = (
        ('Bitcoin', 'Bitcoin'), ('Ethereum', 'Ethereum'),
        ('BNB', 'BNB'), ('CELO', 'CELO'),
        ('Tron', 'Tron'), ('Naira', 'Naira')
    )
    owner = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    address = models.CharField(max_length=555, null=True, blank=True)
    account_name = models.CharField(max_length=255, null=True)
    bank_name = models.CharField(max_length=255, null=True)
    private_key = models.CharField(max_length=555, null=True, blank=True)
    xpub = models.CharField(max_length=555, null=True, blank=True)
    mnemonic = models.CharField(max_length=555, null=True, blank=True)
    network = models.CharField(
        max_length=555, choices=network_choice,
        null=True, blank=True
    )
    balance = models.FloatField(default=0.0)
    qrcode = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.owner.email +": "+ self.network
    
    def get_balance(self):
        return self.balance
    
    def deposit(self, amount: float):
        if self.network == "naira":
            self.balance += amount
            self.save()
            return self.balance
    
        client = Blockchain(os.getenv("TATUM_API_KEY"))
    
        admin_wallet = Wallet.objects.get(owner__username="superman-houseboy", network=self.network.title())
        private_key = client.decrypt_crendentails(admin_wallet.private_key)

        return client.send_token(
            self.address, self.network.lower(),
            amount, private_key, admin_wallet.address
        )
    
    def notify_withdraw_handler(self, amount, account_number):
        try:
            bank = Payout.objects.get(account_number=account_number, user=self.owner)
        except Payout.DoesNotExist:
            raise ValueError("No payout exists with that account number")
        subject = f"Withdrawal request from {bank.user.email}"
        message = f"""{bank.user.email} has requested to withdraw the sum
        of {amount}.
        Here are the bank details:

        Bank name: {bank.bank_name}
        Account name: {bank.account_name}
        Account number: {account_number}
        """
        mail.send_mail(
            subject, message, "info@bitgifty.com",
            [
                "wasiuadegoke14@gmail.com", "princewillolaiya@gmail.com",
                "mybitgifty@gmail.com", "adedolapom@gmail.com"
            ]
        )
    
    def deduct(self, amount: float):
        if self.network == "naira":
            if self.balance < amount:
                raise ValueError("Insufficient balance") 
            self.balance -= amount
            self.save()
            return self.balance
    
        client = Blockchain(os.getenv("TATUM_API_KEY"))
    
        admin_wallet = Wallet.objects.get(owner__username="superman-houseboy", network=self.network.title())
        private_key = client.decrypt_crendentails(self.private_key)
        return client.send_token(
            admin_wallet.address, self.network.lower(),
            amount, private_key, self.address
        )

    def create_giftcard(self, amount):
        client = Blockchain(os.getenv("TATUM_API_KEY"))
        try:
            fee = GiftCardFee.objects.get(network=self.network.title(), operation="create").amount
        except Exception:
            fee = 0.0
        admin_wallet = Wallet.objects.filter(
            owner__username="superman-houseboy",
            network=self.network.title()
        ).first()

        charge = float(amount + fee)
        
        try:
            return client.create_gift_card(
                self.private_key, charge,
                admin_wallet.address,
                self.network.lower(), self.address
            )
        except Exception as exception:
            raise ValueError(exception)

    def redeem_giftcard(self, code):
        try:
            giftcard = GiftCard.objects.get(code=code)
        except GiftCard.DoesNotExist:
            raise ValueError("gift card not found")

        try:
            fee = GiftCardFee.objects.get(network=giftcard.currency.title(), operation="redeem").amount
        except GiftCardFee.DoesNotExist:
            fee = 0.0

        if giftcard.status == "used":
            raise ValueError("Giftcard has already been used")

        TATUM_API_KEY = os.getenv("TATUM_API_KEY")
        client = Blockchain(TATUM_API_KEY, os.getenv("BIN_KEY"), os.getenv("BIN_SECRET"))
        admin_wallet = Wallet.objects.get(owner__username="superman-houseboy", network=giftcard.currency.title())
        amount = str(giftcard.amount - fee)
    
        return client.redeem_gift_card(
            code, admin_wallet.private_key, amount,
            self.address, giftcard.currency.lower(), admin_wallet.address
        )
    class Meta:
        unique_together = ('owner', 'network')

