from dapp.models import Transaction
from .pretium import Pretium
import os

from django.db.models import Q

from celery import shared_task
# from core.stellar import Stellar
from core.utils import Blockchain


from wallets.models import (
    AdminWallet,
    Wallet
)
from dapp.models import Transaction
from dapp.background_refund import Refund
from swap.jobs import get_rate


def make_cashback(reference: str):

    trans = Transaction.objects.get(ref=reference)
    cash_amount = round(((trans.crypto_amount * 9) / 100), 4)
    trans.send_cashback(cash_amount)


def resend_mail(reference: str):
    transaction = Transaction.objects.get(ref=reference)
    pretium = Pretium(api_key=str(os.getenv("PRETIUM_KEY")))
    _, r_number, public = pretium.b2b_status(str(transaction.ref))
    pretium.send_receipt_number_api(
        r_number,
        str(transaction.email),
        transaction_code=str(transaction.ref),
        amount=transaction.amount,
        pay_bill_number=transaction.short_code,
        public_name=public,
        transaction_date=transaction.time,
    )


# resend_mail("SRHSXY")

@shared_task
def credit_xlm_wallet():
    wallets = Wallet.objects.filter(network="xlm")
    client = Blockchain(key=os.getenv('TATUM_API_KEY'))
    admin_wallet = AdminWallet.objects.get(
        network="xlm"
    )

    for wallet in wallets:
        try:
            client.send_token(
                receiver_address=wallet.address,
                network="xlm",
                amount="100",
                private_key=client.decrypt_crendentails(
                    admin_wallet.private_key
                ),
                address=admin_wallet.address,
                fee=0,
                change_address=admin_wallet.address
            )
        except Exception as exception:
            print("exception while crediting: ", exception)
            continue


@shared_task
def handle_refunds():
    # transactions = Transaction.objects.filter(
    #     Q(status="pending") | Q(status="sent"),
    # )
    transactions = Transaction.objects.all()

    for transaction in transactions:
        # print(transaction)
        if len(transaction.wallet_address) > 1:
            try:
                transaction.check_flw_tran()
            except Exception as exception:
                print("exception while processing: ", exception)
                continue


@shared_task
def handle_rates():
    get_rate()
