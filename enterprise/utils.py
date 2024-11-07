from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from core.utils import Blockchain


class Email(object):
    def __init__(self, template: str = ""):
        self.template = template

    def send(subject: str, tags: dict, address: str):
        html_message = render_to_string(
            'transaction_success.html',
            tags
        )
        plain_message = strip_tags(html_message)
        mail.send_mail(
            subject, plain_message, "BitGifty <info@bitgifty.com>",
            [address], html_message=html_message
        )

    def send_plain(subject: str, message: str, addresses: list):
        mail.send_mail(
            subject, message, "BitGifty <info@bitgifty.com>",
            addresses
        )


class Wallet(object):
    def __init__(self, tatum_key):
        self.tatum_key = tatum_key
        self.client = Blockchain(key=tatum_key)

    def get_network(self, currency: str, account_type: str):
        network_mapping = {
            "bitcoin": {
                "virt": "BTC",
                "wallet": "Bitcoin",
            },
            "celo": {
                "virt": "CELO",
                "wallet": "Celo",
            },
            "naira": {
                "virt": "VC__BITGIFTY_NAIRA",
                "wallet": "VC__BITGIFTY_NAIRA",
            },
            "ceur": {
                "virt": "CEUR",
                "wallet": "celo",
            },
            "cusd": {
                "virt": "CUSD",
                "wallet": "celo",
            },
            "usdt_tron": {
                "virt": "USDT_TRON",
                "wallet": "tron"
            },
            "tron": {
                "virt": "TRON",
                "wallet": "tron"
            },
            "eth": {
                "virt": "ETH",
                "wallet": "ethereum"
            },
        }

        return network_mapping[currency][account_type]

    def send_instant(
        self, sender_id: str, receiver_id: str, amount: float,
            note: str):

        self.client.send_instant(
            sender_id,
            receiver_id,
            amount,
            sender_note=note,
            recipient_note=note
        )
        return
