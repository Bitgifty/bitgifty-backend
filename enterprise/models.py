import os

from django.db import models

from core.utils import FlutterWave
from wallets.models import VirtualAccount
from .utils import Email, Wallet

# Create your models here.


class Transaction(models.Model):
    amount = models.FloatField(default=0.0)
    currency = models.CharField(max_length=255, default="naira")
    currency_type = models.CharField(max_length=255, default="fiat")
    crypto_amount = models.FloatField(default=0.0)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    account_name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default='pending')
    time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    transaction_type = models.CharField(max_length=255, null=True)
    transaction_hash = models.CharField(max_length=255, null=True)
    wallet_address = models.CharField(max_length=255, null=True)
    email = models.EmailField(blank=True, null=True)
    ref = models.CharField(max_length=255, null=True, blank=True)
    customer = models.CharField(blank=True, null=True, max_length=255)
    biller_code = models.CharField(blank=True, null=True, max_length=255)
    item_code = models.CharField(blank=True, null=True, max_length=255)
    bill_type = models.CharField(blank=True, null=True, max_length=255)
    country = models.CharField(
        blank=True, null=True, default="NG",
        max_length=255)
    user = models.ForeignKey(
        'accounts.Account', on_delete=models.CASCADE,
        related_name="enterprise_user"
    )

    def __str__(self):
        return f"{self.wallet_address}: {self.email}"

    def check_trans_status(self):
        email = self.email
        token_data = ""

        status = "failed"

        wallet_client = Wallet(tatum_key=os.getenv("TATUM_API_KEY"))

        network = wallet_client.get_network("naira", "virt")

        admin_virt = VirtualAccount.objects.get(
                owner__username="superman-houseboy",
                chain=network
            )

        user_virt = VirtualAccount.objects.get(
            owner=self.user,
            chain=network
        )

        if self.ref:
            if self.country != "KE":
                flw_client = FlutterWave(api_key=self.user.flw_key)
                status = flw_client.get_payment_status(self.ref).get("status")
                token_data = flw_client.get_payment_status(
                    self.ref
                ).get('data')

        if token_data:
            token = token_data.get('extra')

        if status == "success":
            if self.country != "KE":
                if token_data.get('extra'):
                    # todo: customize email
                    subject = "Here's your Electricity Prepaid\
                        Token - Payment Successful"
                    tags = {'token': token}

                    mail = Email('transaction_success.html')
                    mail.send(subject, tags, email)
                    self.status = "success"

            wallet_client.send_instant(
                user_virt.account_id,
                admin_virt.account_id,
                self.amount,
                note="refund",
            )

        if status == "error" or status == "failed":
            self.status = "failed"
            if self.email:
                subject = "Bill payment failed"
                tags = {
                    'receipent_email': email,
                    'amount': self.amount,
                    'currency': self.currency,
                }

                mail = Email("transaction_failed.html")
                mail.send(subject, tags, self.email)

        self.status = status
        self.save()
