import os

from django.db import models
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import mail, exceptions

from giftCards.models import GiftCardImage, GiftCardFee

from core.utils import Blockchain
from .background_refund import Refund


# Create your models here.

# Create Get Fee endpoint


class GiftCard(models.Model):
    address = models.CharField(max_length=255)
    currency = models.CharField(max_length=255)
    amount = models.FloatField(default=0.0)
    image = models.ForeignKey(
        GiftCardImage, on_delete=models.SET_NULL,
        null=True, related_name="dapp_image"
    )
    sender_email = models.EmailField(null=True, blank=True)
    receipent_email = models.EmailField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default="generated")
    creation_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.currency

    def save(self, *args, **kwargs):
        try:
            if self._state.adding:
                client = Blockchain(key=str(os.getenv("TATUM_API_KEY")))
                self.code = client.generate_code()
                if self.receipent_email:
                    subject = "Gift Card from BitGifty"
                    note = "You received a gift card from a friend"
                    if self.note:
                        note = self.note
                    html_message = render_to_string(
                        "giftcardtemplate_v2.html",
                        {
                            "image": self.image.link,
                            "receipent_email": self.receipent_email,
                            "sender_email": self.sender_email,
                            "code": self.code,
                            "note": note,
                            "amount": self.amount,
                            "currency": self.currency,
                        },
                    )

                    plain_message = strip_tags(html_message)
                    mail.send_mail(
                        subject,
                        plain_message,
                        "BitGifty <dev@bitgifty.com>",
                        [self.receipent_email],
                        html_message=html_message,
                    )
        except Exception as exception:
            raise exceptions.ValidationError(str(exception))
        return super(GiftCard, self).save(*args, **kwargs)


class Redeem(models.Model):
    address = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    redemption_date = models.DateTimeField(auto_now_add=True, null=True)

    def redeem_giftcard(self, code):
        network_mapping = {
            "celo": {
                "virt": "celo",
                "wallet": "celo",
            },
            "ceur": {
                "virt": "CEUR",
                "wallet": "celo",
            },
            "cusd": {
                "virt": "CUSD",
                "wallet": "celo",
            },
            "stellar_usdc": {
                "virt": "STELLAR_USDC",
                "wallet": "xlm",
            },
            "usdt_tron": {"virt": "USDT_TRON", "wallet": "tron"},
            "tron": {"virt": "TRON", "wallet": "tron"},
            "eth": {"virt": "ETH", "wallet": "ethereum"},
        }
        try:
            giftcard = GiftCard.objects.get(code=code)
        except GiftCard.DoesNotExist:
            raise ValueError("Giftcard not found")

        if giftcard.status == "used":
            raise ValueError("Giftcard has already been used")

        try:
            fee = GiftCardFee.objects.get(
                network=giftcard.currency.title(), operation="redeem"
            ).amount
        except GiftCardFee.DoesNotExist:
            fee = 0.0

        TATUM_API_KEY = str(os.getenv("TATUM_API_KEY"))

        client = Blockchain(
            TATUM_API_KEY, str(os.getenv("BIN_KEY")),
            str(os.getenv("BIN_SECRET"))
        )

        try:
            admin_wallet = AdminWallet.objects.get(
                owner__username=f"{os.getenv('ADMIN_USERNAME')}",
                network__iexact=network_mapping[
                    giftcard.currency.lower()
                ]["wallet"],
            )
        except AdminWallet.DoesNotExist:
            raise ValueError("Admin Wallet not found")

        amount = str(float(giftcard.amount) - fee)

        try:
            return client.redeem_gift_card(
                code,
                str(admin_wallet.private_key),
                amount,
                self.address,
                giftcard.currency.lower(),
                str(admin_wallet.address),
            )
        except Exception as exception:
            raise exceptions.ValidationError(str(exception), str(400))

    def save(self, *args, **kwargs):
        if self._state.adding:
            try:
                giftcard = GiftCard.objects.get(code=self.code)
            except GiftCard.DoesNotExist:
                raise exceptions.ValidationError(
                    "Giftcard does not exist", "404"
                )

            note = giftcard.note

            try:
                self.redeem_giftcard(self.code)
            except Exception as exception:
                raise exceptions.ValidationError(str(exception), code="400")

            giftcard.status = "used"

            giftcard.save()

            subject = "Gift Card Redeemed"
            html_message = render_to_string(
                "giftcard_redeem_v2.html",
                {
                    "receipent_email": giftcard.receipent_email,
                    "code": self.code,
                    "note": note,
                },
            )

            plain_message = strip_tags(html_message)
            mail.send_mail(
                subject,
                plain_message,
                f"BitGifty <{os.getenv('ADMIN_EMAIL')}>",
                [str(giftcard.receipent_email)],
                html_message=html_message,
            )
        return super(Redeem, self).save(*args, **kwargs)


class Transaction(models.Model):
    amount = models.FloatField(default=0.0)
    currency = models.CharField(max_length=255, default="naira")
    currency_type = models.CharField(max_length=255, default="fiat")
    crypto_amount = models.FloatField(default=0.0)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    account_name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default="pending")
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
        blank=True, null=True, default="NG", max_length=255
    )
    short_code = models.CharField(max_length=255, null=True, blank=True)
    error_message = models.TextField(null=True)
    token = models.TextField(null=True)
    transfer_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.wallet_address}: {self.email} -> {self.status}"

    def send_token_email(self):
        if self.token:
            subject = "Here's your Electricity Prepaid\
                Token - Payment Successful"
            html_message = render_to_string(
                "transaction_success.html",
                {
                    "token": self.token,
                },
            )
            plain_message = strip_tags(html_message)
            mail.send_mail(
                subject,
                plain_message,
                "BitGifty <info@bitgifty.com>",
                [str(self.email)],
                html_message=html_message,
            )

    def send_cashback(self, amount):
        try:
            cashback = CashBack(
                amount=amount,
                wallet=self.wallet_address, percentage=10
            )
            cashback.save()
            transaction = Transaction(
                amount=self.amount,
                currency="cusd",
                currency_type="crypto",
                crypto_amount=round(amount, 4),
                status="success",
                transaction_type="cashback",
                email=self.email,
                wallet_address=self.wallet_address,
                transaction_hash=cashback.transaction_hash,
                bill_type=self.bill_type,
                biller_code=self.biller_code,
                item_code=self.item_code,
                ref=self.ref,
                customer=self.customer,
                country=self.country,
            )
            transaction.save()
        except Exception as exception:
            print("cashback exception: ", exception)

    def send_receipt(
            self, subject: str, message: str,
            from_email: str, recipient: str
            ):
        subject = subject
        message = message
        from_email = from_email
        recipient = recipient
        mail.send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[recipient],
        )

    def check_flw_tran(self):
        refund = Refund()
        # if no reference
        if self.ref == "invalid":
            status = "error"
        elif "sus" == str(self.ref)[:3]:
            return
        else:
            # get status
            try:
                status = refund.get_status(self)
            except Exception as exception:
                print(exception)
                status = "error"

        # if status is error or failed
        if status == "error" or status == "failed" or status == "missing":
            admin_wallet = AdminWallet.objects.get(
                owner__username="superman-houseboy", network__iexact="celo"
            )
            prev_refund = Transaction.objects.filter(
                ref=self.ref
            ).count()

            if prev_refund == 1:
                refund.send_failed_notif_email(self)
                txid = refund.refund(self, admin_wallet)
                # txid = None
                if txid:
                    transact = Transaction(
                        amount=self.amount,
                        currency=self.currency,
                        currency_type="crypto",
                        crypto_amount=self.crypto_amount,
                        status="success",
                        transaction_type="refund",
                        email=self.email,
                        wallet_address=self.wallet_address,
                        transaction_hash=txid.get("txId"),
                        bill_type=self.bill_type,
                        biller_code=self.biller_code,
                        item_code=self.item_code,
                        ref=self.ref,
                        customer=self.customer,
                        country=self.country,
                    )
                    transact.save()
            else:
                print("double: ", self.ref)
        if status == "success":
            # if success, send token and cashback where
            # applicable
            self.send_token_email()

            # cash amount is money to send it is 9% of crypto amount
            cash_amount = round(((self.crypto_amount * 9) / 100), 4)

            # check if crypto amount is greater than 0.9
            if self.crypto_amount >= 0.9:
                # check if crypto amount is greater than 5
                if self.crypto_amount > 5:
                    # limit cash amount to 0.5
                    cash_amount = round(((5 * 10) / 100), 4)

                self.send_cashback(cash_amount)

            if self.bill_type == "FLW_TRANSFER":
                self.send_receipt(
                    subject="Transfer Reciept",
                    message="You initiated a transfer",
                    from_email="info@bitgifty.com",
                    recipient=str(self.email),
                )

        if status == "missing":
            status = "failed"
        self.status = status
        self.save()


class AdminWallet(models.Model):
    owner = models.ForeignKey(
        "accounts.Account", on_delete=models.CASCADE, related_name="dapp_owner"
    )
    address = models.CharField(max_length=555, null=True, blank=True)
    private_key = models.CharField(max_length=555, null=True, blank=True)
    xpub = models.CharField(max_length=555, null=True, blank=True)
    mnemonic = models.CharField(max_length=555, null=True, blank=True)
    network = models.CharField(max_length=555, null=True, blank=True)
    balance = models.FloatField(default=0.0)
    qrcode = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.owner.email


class Reward(models.Model):
    wallet = models.CharField(max_length=255, unique=True)
    amount = models.FloatField(default=0.25)
    transaction_hash = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "reward: " + self.wallet

    def save(self, *args, **kwargs):
        if self._state.adding:
            sender_wallet = AdminWallet.objects.get(network__iexact="celo")
            client = Blockchain(key=str(os.getenv("TATUM_API_KEY")))
            sender_private_key = client.decrypt_crendentails(
                str(sender_wallet.private_key)
            )
            try:
                data = client.send_token(
                    receiver_address=self.wallet,
                    network="cusd",
                    amount=str(self.amount),
                    private_key=sender_private_key,
                    address=str(sender_wallet.address),
                )
                self.transaction_hash = data.get("txId")
            except Exception:
                raise ValueError("Cashback failed")

        return super(Reward, self).save(*args, **kwargs)


class CashBack(models.Model):
    wallet = models.CharField(max_length=255)
    amount = models.FloatField(default=0.0)
    percentage = models.FloatField(default=10)
    transaction_hash = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "cashback: " + self.wallet

    def save(self, *args, **kwargs):
        if self._state.adding:
            sender_wallet = AdminWallet.objects.get(network__iexact="celo")
            client = Blockchain(key=str(os.getenv("TATUM_API_KEY")))
            sender_private_key = client.decrypt_crendentails(
                str(sender_wallet.private_key)
            )

            try:
                data = client.send_token(
                    receiver_address=self.wallet,
                    network="cusd",
                    amount=str(self.amount),
                    private_key=sender_private_key,
                    address=str(sender_wallet.address),
                )
                self.transaction_hash = data.get("txId")
                print("cashback hash: ", self.transaction_hash)
            except Exception as exception:
                print("cashback exception: ", exception)
                raise ValueError("Cashback failed")

        return super(CashBack, self).save(*args, **kwargs)


class StellarTransaction(models.Model):
    amount = models.FloatField(default=0.0)
    currency = models.CharField(max_length=255, default="naira")
    currency_type = models.CharField(max_length=255, default="fiat")
    crypto_amount = models.FloatField(default=0.0)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    account_name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default="pending")
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
        blank=True, null=True, default="NG", max_length=255
    )
    short_code = models.CharField(max_length=255, null=True, blank=True)
    error_message = models.TextField(null=True)
    token = models.TextField(null=True)

    def __str__(self):
        return f"{self.wallet_address}: {self.email} -> {self.status}"

    def send_token_email(self):
        if self.token:
            subject = "Here's your Electricity Prepaid\
                Token - Payment Successful"
            html_message = render_to_string(
                "transaction_success.html",
                {
                    "token": self.token,
                },
            )
            plain_message = strip_tags(html_message)
            mail.send_mail(
                subject,
                plain_message,
                "BitGifty <info@bitgifty.com>",
                [str(self.email)],
                html_message=html_message,
            )

    def send_cashback(self, amount):
        try:
            cashback = CashBack(
                amount=amount,
                wallet=self.wallet_address, percentage=10
            )
            cashback.save()
            transaction = StellarTransaction(
                amount=self.amount,
                currency="usdc",
                currency_type="crypto",
                crypto_amount=round(amount, 4),
                status="success",
                transaction_type="cashback",
                email=self.email,
                wallet_address=self.wallet_address,
                transaction_hash=cashback.transaction_hash,
                bill_type=self.bill_type,
                biller_code=self.biller_code,
                item_code=self.item_code,
                ref=self.ref,
                customer=self.customer,
                country=self.country,
            )
            transaction.save()
        except Exception as exception:
            print("cashback exception: ", exception)

    def send_receipt(
            self, subject: str, message: str,
            from_email: str, recipient: str
            ):
        subject = subject
        message = message
        from_email = from_email
        recipient = recipient
        mail.send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[recipient],
        )

    def check_flw_tran(self):
        refund = Refund()
        # if no reference
        if self.ref == "invalid":
            status = "error"
        elif "sus" == str(self.ref)[:3]:
            return
        else:
            # get status
            print("checking.........")
            try:
                status = refund.get_status(self)
            except Exception as exception:
                print("except: ", exception)
                status = "error"
            print("checked........: ", status)

        print("status: ", status)
        # if status is error or failed
        if status == "error" or status == "failed" or status == "missing":
            print("here 1")
            admin_wallet = AdminWallet.objects.get(
                owner__username="superman-houseboy", network__iexact="stellar_usdc"
            )
            print("here 2")
            prev_refund = Transaction.objects.filter(
                ref=self.ref
            ).count()

            if prev_refund == 1:
                refund.send_failed_notif_email(self)
                txid = refund.refund(self, admin_wallet)
                print("txid >>>>>>>>>>> ", txid)
                if txid:
                    transact = StellarTransaction(
                        amount=self.amount,
                        currency=self.currency,
                        currency_type="crypto",
                        crypto_amount=self.crypto_amount,
                        status="success",
                        transaction_type="refund",
                        email=self.email,
                        wallet_address=self.wallet_address,
                        transaction_hash=txid.get("txId"),
                        bill_type=self.bill_type,
                        biller_code=self.biller_code,
                        item_code=self.item_code,
                        ref=self.ref,
                        customer=self.customer,
                        country=self.country,
                    )
                    transact.save()
                print("got 111")
            else:
                print("double: ", self.ref)
        if status == "success":
            # if success, send token and cashback where
            # applicable
            self.send_token_email()

            if self.bill_type == "FLW_TRANSFER":
                self.send_receipt(
                    subject="Transfer Reciept",
                    message="You initiated a transfer",
                    from_email="info@bitgifty.com",
                    recipient=str(self.email),
                )

        if status == "missing":
            status = "failed"
        self.status = status
        self.save()


class StellarGiftCard(models.Model):
    wallet = models.CharField(max_length=255)
    currency = models.CharField(max_length=255)
    amount = models.FloatField(default=0.0)
    image = models.ForeignKey(
        GiftCardImage, on_delete=models.SET_NULL,
        null=True
    )
    receipent_email = models.EmailField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default="generated")
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    transaction_hash = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.currency

    def save(self, *args, **kwargs):
        try:
            if self._state.adding:
                if self.receipent_email:
                    subject = "Gift Card from BitGifty"
                    note = "You received a gift card from a friend"

                    if self.note:
                        note = self.note

                    html_message = render_to_string(
                        'giftcardtemplate_v2.html',
                        {
                            'image': self.image.link,
                            'receipent_email': self.receipent_email,
                            'code': self.code,
                            'note': note,
                            'amount': self.amount,
                            'currency': self.currency,
                        }
                    )

                    plain_message = strip_tags(html_message)
                    mail.send_mail(
                        subject, plain_message, "BitGifty <dev@bitgifty.com>",
                        [self.receipent_email], html_message=html_message
                    )
        except Exception as exception:
            raise ValueError(exception)
        return super(StellarGiftCard, self).save(*args, **kwargs)


class RedeemStellar(models.Model):
    wallet = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    redemption_date = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        try:
            if self._state.adding:
                giftcard = StellarGiftCard.objects.get(code=self.code)
                note = giftcard.note
                giftcard.status = "used"
                giftcard.save()

                subject = "Gift Card Redeemed"
                html_message = render_to_string(
                    'giftcard_redeem_v2.html',
                    {
                        'receipent_email': giftcard.receipent_email,
                        'code': self.code,
                        'note': note,
                    }
                )

                plain_message = strip_tags(html_message)
                mail.send_mail(
                    subject, plain_message, "BitGifty <dev@bitgifty.com>",
                    [giftcard.receipent_email], html_message=html_message
                )
        except Exception as exception:
            raise ValueError(exception)
        return super(RedeemStellar, self).save(*args, **kwargs)
