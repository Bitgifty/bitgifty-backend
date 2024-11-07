import requests
import os
from django.core.exceptions import ValidationError
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import mailtrap as mt


class Pretium(object):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.url = "https://pretium.africa/api/v1/"

    def get_url(self) -> str:
        return self.url

    def get_airtime_url(self):
        return self.url + "utilities/airtime/buy"

    def get_data_url(self):
        return self.url + "utilities/data/buy"

    def get_airtime_status_url(self):
        return self.url + "utilities/airtime/transaction"

    def get_data_status_url(self):
        return self.url + "utilities/data/transaction"

    def get_b2b_confirm_url(self):
        return self.url + "payment/b2b/prompt/status"

    def get_data_packages_url(self):
        return self.url + "utilities/data/packages"

    def get_network_url(self) -> str:
        return self.url + "payment/mobile-networks"

    def get_headers(self) -> dict:
        headers = {
            "api-key": self.api_key
        }

        return headers

    def get_b2b_url(self) -> str:
        return self.url + "payment/b2b/"

    def get_airtime_code(self, country: str) -> str:
        code_repo = {
            "KE": "k7myt",
            "ZA": "sndnw",
            "UG": "dru0s"
        }
        return code_repo[country]

    def get_data_code(self, country: str) -> str:
        code_repo = {
            "KE": "vigag",
            "ZA": "sndnw",
            "UG": "dru0s"
        }
        return code_repo[country]

    def buy_airtime(
            self, amount: int,
            phone_number: str, country: str) -> tuple[dict, str]:
        body = {
            "code": self.get_airtime_code(country),
            "amount": amount,
            "mobile": phone_number,
            "payment_method": "FIAT",
            "callback_url": ""
        }

        req = requests.post(
            url=self.get_airtime_url(),
            headers={
                "api-key": os.getenv("PRETIUM_KEY")
            },
            data=body
        )

        response = req.json()

        if response.get("code") >= 300:
            raise ValidationError("airtime request failed")

        trans_code = response.get("data").get("transaction_code")

        if len(trans_code) < 1:
            raise ValidationError("invalid transaction code")

        return response, trans_code

    def buy_data(self, amount: int, phone_number: str, data_package_id: int):

        body = {
            "data_package_id": data_package_id,
            "amount": amount,
            "mobile": phone_number,
            "payment_method": "FIAT",
            "callback_url": ""
        }

        req = requests.post(
            url=self.get_data_url(),
            headers={
                "api-key": os.getenv("PRETIUM_KEY")
            },
            data=body
        )

        response = req.json()

        if response.get("code") != 200:
            raise ValidationError("data request failed")
        trans_code = response.get("data").get("transaction_code")

        if len(trans_code) < 1:
            raise ValidationError("invalid transaction code")

        return response, trans_code

    def get_mobile_networks(self, country: str):
        body = {
            "country_name": country,
        }

        req = requests.post(
            url=self.get_network_url(),
            headers={
                "api-key": os.getenv("PRETIUM_KEY")
            },
            data=body
        )

        response = req.json()
        if response.get("code") != 200:
            raise ValidationError("request failed")

        return response

    def get_data_packages(self, mobile_network_id: int):
        body = {
            "mobile_network_id": mobile_network_id,
        }

        req = requests.post(
            url=self.get_data_packages_url(),
            headers={
                "api-key": os.getenv("PRETIUM_KEY")
            },
            data=body
        )

        response = req.json()

        if response.get("code") != 200:
            raise ValidationError("request failed")

        return response

    def check_transaction(self, transaction_code: str, bill_type: str) -> str:
        body = {
            "code": transaction_code,
        }

        url = self.get_airtime_status_url()

        if bill_type == "MOBILEDATA":
            url = self.get_data_status_url()

        req = requests.post(
            url=url,
            headers=self.get_headers(),
            data=body
        )

        response = req.json()

        if response.get("code") != 200:
            raise ValidationError("airtime request failed", 200)

        if bill_type == "MOBILEDATA":
            status = response.get("data").get("is_sent")
        else:
            status = response.get("data").get("status")

        if len(status) < 1:
            raise ValidationError("invalid request")

        return status

    def build_pay_body(
            self, amount: int, short_code: str,
            account_number: str):
        body = {
            "code": "9sbsr",
            "amount": amount,
            "payment_method": "FIAT",
            "type": "PAYBILL",
            "shortcode": short_code,
            "account_number": account_number,
            "callback_url": ""
        }

        return body

    def build_buy_body(
            self, amount: int, short_code: str,
            account_number: str):
        body = {
            "code": "9sbsr",
            "amount": amount,
            "payment_method": "FIAT",
            "type": "BUY_GOODS",
            "shortcode": short_code,
            "account_number": account_number,
            "callback_url": ""
        }

        return body

    def prompt(self, body: dict):

        req = requests.post(
            url=self.get_b2b_url() + "prompt",
            headers={
                "api-key": os.getenv("PRETIUM_KEY")
            },
            data=body
        )
        response = req.json()

        if response.get("code") != 200:
            raise ValidationError("request failed")

        return response

    def prompt_confirm(self, transaction_code: str):
        body = {
            "memo": transaction_code,
        }

        req = requests.post(
            url=self.get_b2b_url() + "prompt/confirm",
            headers={
                "api-key": os.getenv("PRETIUM_KEY")
            },
            data=body
        )

        response = req.json()

        if response.get("code") != 200:
            raise ValidationError("request failed")

        return response

    def b2b_transactions(self):
        body = {}

        req = requests.post(
            url=self.get_b2b_url() + "transactions",
            headers={
                "api-key": os.getenv("PRETIUM_KEY")
            },
            data=body
        )

        response = req.json()

        if response.get("code") != 200:
            raise ValidationError("request failed")

        response = self.prompt(body=body)
        return response.get(
            "message"
        ),
        response.get("data").get("transaction_code")

    def buy_goods(self, amount: int, short_code: int, account_number: str):
        body = self.build_buy_body(
            amount=amount,
            short_code=short_code,
            account_number=account_number
        )

        response = self.prompt(body=body)
        return (
            response.get("message"),
            response.get("data").get("transaction_code"))

    def pay_bill(self, amount: int, short_code: int, account_number: str):
        body = self.build_pay_body(
            amount=amount,
            short_code=short_code,
            account_number=account_number
        )

        response = self.prompt(body=body)
        return (
            response.get("message"),
            response.get("data").get("transaction_code"))

    def b2b_status(self, code: str):
        body = {"transaction_code": code}

        req = requests.post(
            url=self.get_b2b_confirm_url(),
            headers={
                "api-key": os.getenv("PRETIUM_KEY")
            },
            data=body
        )

        response = req.json()

        if response.get("code") != 200:
            raise ValidationError("request failed")

        return (
            response.get("data").get("is_disbursed"),
            response.get("data").get("receipt_number"),
            response.get("data").get("public_name")
        )

    def send_receipt_number(
            self, receipt_number: str, email: str,
            transaction_code: str = "", amount: str = "",
            pay_bill_number: str = "", public_name: str = "",
            transaction_date=""
            ):
        subject = "Receipt Number"
        html_message = render_to_string(
            'receipt_number.html',
            {
                'transaction_code': transaction_code,
                'amount': amount,
                'pay_bill_number': pay_bill_number,
                'public_name': public_name,
                'receipt_number': receipt_number,
                'transaction_date': transaction_date,
            }
        )
        plain_message = strip_tags(html_message)
        mail.send_mail(
            subject, plain_message, "BitGifty <info@bitgifty.com>",
            [email], html_message=html_message
        )

    def send_receipt_number_api(
            self, receipt_number: str, email: str,
            transaction_code: str = "", amount: str = "",
            pay_bill_number: str = "", public_name: str = "",
            transaction_date=""
            ):
        subject = "Receipt Number"
        html_message = render_to_string(
            'receipt_number.html',
            {
                'transaction_code': transaction_code,
                'amount': amount,
                'pay_bill_number': pay_bill_number,
                'public_name': public_name,
                'receipt_number': receipt_number,
                'transaction_date': transaction_date,
            }
        )
        plain_message = strip_tags(html_message)
        mail = mt.Mail(
            sender=mt.Address(email="info@bitgifty.com", name="Bitgifty"),
            to=[mt.Address(email=email)],
            subject=subject,
            text=plain_message,
            category="Receipt",
            html=html_message,
        )

        client = mt.MailtrapClient(token=str(os.getenv("EMAIL_HOST_PASSWORD")))
        response = client.send(mail)

