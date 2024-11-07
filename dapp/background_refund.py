import os
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import mail

from core.flutterwave import FlutterWave
from core.pretium import Pretium
from core.bet9ja import Bet9ja
from core.utils import Blockchain


class Refund(object):
    flw = FlutterWave(key=os.getenv("FLW_ALT_KEY"))
    pretium = Pretium(api_key=str(os.getenv("PRETIUM_KEY")))
    bet9ja = Bet9ja(
        accountid=os.getenv("BET9JA_ACCOUNT_ID"),
        username=os.getenv("BET9JA_USERNAME"),
        password=os.getenv("BET9JA_PASSWORD"),
        secret_key=os.getenv("BET9JA_SECRET"),
    )
    blockchain = Blockchain(key=str(os.getenv("TATUM_API_KEY")))

    def get_status(self, transaction):
        country = transaction.country
        status = transaction.status

        if country == "NG" or country == "GH":
            if transaction.bill_type == "UTILITYBILLS":
                flw_response = self.flw.fetch_transaction(transaction.ref)
                status = flw_response.get("status")
                if status == "success":
                    if flw_response.get("data"):
                        token = flw_response['data']['extra']
                        transaction.status = "success"
                        transaction.token = token
                        transaction.save()
            elif transaction.bill_type == "BET9JA_TOPUP":
                try:
                    bet = self.bet9ja.check_transaction(transaction.ref)
                    bet_status = bet.get("data").get("TransactionStatus")
                    if bet_status == "1":
                        status = "success"
                    if bet_status == "0":
                        status = "pending"
                    if bet_status == "-1":
                        status = "failed"
                except Exception:
                    status = "error"
            elif transaction.bill_type == "FLW_TRANSFER":
                flw_response = self.flw.fetch_transfer(transaction.transfer_id)
                status = flw_response
            else:
                flw_response = self.flw.fetch_transaction(transaction.ref)
                status = flw_response.get("status")
        else:
            if (
                "BUY_GOODS" in transaction.bill_type
                or "PAYBILL" in transaction.bill_type
            ):
                status, receipt_number, public_name = self.pretium.b2b_status(
                    transaction.ref
                )

                status = status.lower()
                if status == "complete":
                    status = "success"
                elif status != "failed":
                    status = "pending"
                else:
                    status = "failed"

                if receipt_number:
                    self.send_receipt_number(
                        receipt_number=receipt_number,
                        public_name=public_name,
                        transaction=transaction
                    )
            else:
                status = self.pretium.check_transaction(
                    transaction.ref, transaction.bill_type
                ).lower()

        return status

    def send_receipt_number(
            self, receipt_number: str,
            public_name: str, transaction):
        try:
            self.pretium.send_receipt_number(
                receipt_number,
                transaction.email,
                transaction_code=transaction.ref,
                amount=transaction.amount,
                pay_bill_number=transaction.short_code,
                public_name=public_name,
                transaction_date=transaction.time,
            )
        except Exception as exception:
            print("receipt: ", exception)

    def send_failed_notif_email(self, transaction):
        if transaction.email:
            subject = "Bill payment failed"
            html_message = render_to_string(
                "transaction_failed.html",
                {
                    "receipent_email": transaction.email,
                    "amount": transaction.crypto_amount,
                    "currency": transaction.currency,
                },
            )
            plain_message = strip_tags(html_message)
            mail.send_mail(
                subject,
                plain_message,
                "BitGifty <info@bitgifty.com>",
                [transaction.email],
                html_message=html_message,
            )

    def refund(self, transaction, admin_wallet):

        network_mapping = {
            "celo": {
                "virt": "CELO",
                "wallet": "Celo",
            },
            "ceur": {
                "virt": "CEUR",
                "wallet": "celo",
            },
            "cusd": {
                "virt": "CUSD",
                "wallet": "cusd",
            },
        }

        try:
            send = self.blockchain.send_token(
                receiver_address=transaction.wallet_address,
                network=network_mapping[transaction.currency]["wallet"],
                amount=str(round(transaction.crypto_amount, 3)),
                private_key=self.blockchain.decrypt_crendentails(
                    admin_wallet.private_key
                ),
                address=admin_wallet.address,
            )
            return send
        except Exception as exception:
            subject = "Refund failed"
            print("failed")

            plain_message = f"""
                {transaction.ref}
                Refund failed for: {transaction.wallet_address},
                {transaction.crypto_amount} {transaction.currency},
                {transaction.email} \n {exception}"""
            mail.send_mail(
                subject,
                plain_message,
                "BitGifty <info@bitgifty.com>",
                ["mybitgifty@gmail.com"],
            )
            return {}
