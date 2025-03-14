import os

from django.db import models
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from giftCards.models import GiftCardFee, GiftCard

from core.utils import Blockchain
from payouts.models import Payout
from .custom_email import send_mass_html_mail
# Create your models here.


class Wallet(models.Model):
    owner = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    address = models.CharField(max_length=555, null=True, blank=True)
    account_name = models.CharField(max_length=255, null=True)
    bank_name = models.CharField(max_length=255, null=True)
    private_key = models.CharField(max_length=555, null=True, blank=True)
    xpub = models.CharField(max_length=555, null=True, blank=True)
    mnemonic = models.CharField(max_length=555, null=True, blank=True)
    network = models.CharField(
        max_length=555,
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
    
    def notify_withdraw_handler(
            self, amount: float, t_type: str,
            bank: Payout = None, wallet= None, reciever_addr: str = None
        ):
        if t_type == "fiat":
            subject1 = f"Withdrawal request from {bank.user.email}"
            str_message1 = f"""{bank.user.email} has requested to withdraw the sum
            of {amount}.
            Here are the bank details:

            Bank name: {bank.bank_name}
            Account name: {bank.account_name}
            Account number: {bank.account_number}
            """
            html_message1 = render_to_string(
                'withdrawal_general.html',
                {
                    "type": "fiat",
                    "subject": subject1,
                    "message": str_message1,
                }
            )
            plain_message1 = strip_tags(html_message1)
            
            str_message2 = f"""You have requested to withdraw the sum
            of {amount}.
            To be paid to the following bank details:

            Bank name: {bank.bank_name}
            Account name: {bank.account_name}
            Account number: {bank.account_number}

            Please be patient while we process your transaction.
            """
            html_message2 = render_to_string(
                'withdrawal_general.html',
                {
                    "type": "fiat",
                    "subject": subject1,
                    "message": str_message2,
                }
            )
            plain_message2 = strip_tags(html_message2)
            message_1 = (
                subject1, plain_message1, html_message1,
                "info@bitgifty.com", ["mybitgifty@gmail.com"]
            )
            message_2 = (
                subject1, plain_message2, html_message2,
                "info@bitgifty.com", [bank.user.email]
            )
            send_mass_html_mail((message_1, message_2), fail_silently=False)

            
        else:
            subject = f"Withdrawal from {wallet.owner.email}"
            str_message = f"""{wallet.owner.email} has withdrawn the sum
            of {amount}{wallet.network.lower()}.
            Here are the wallet details:

            Wallet address: {wallet.address}
            reciever_addr: {reciever_addr}
            """
            html_message = render_to_string(
                'withdrawal_general.html',
                {
                    "type": "crypto",
                    "subject": subject,
                    "message": str_message,
                }
            )
            plain_message = strip_tags(html_message)
            mail.send_mail(
                subject, plain_message, "info@bitgifty.com",
                [wallet.owner.email], html_message=html_message
            )

    
    def deduct(self, amount: float):
        if self.network == "naira":
            if self.balance < amount:
                raise ValueError("Insufficient balance") 
            self.balance -= amount
            self.save()
            return self.balance
    
        client = Blockchain(os.getenv("TATUM_API_KEY"))
        print("******amount", amount)
        print("***type", type(amount))

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

