import requests
import os


class FlutterWave(object):
    def __init__(self, key: str | None):
        self.key = key

    def get_flw_headers(self):
        headers = {
            "Authorization": f"Bearer {self.key}"
        }
        return headers

    def get_transfer_url(self) -> str:
        return "https://api.flutterwave.com/v3/transfers"

    def get_banks(self, country: str):
        if len(country) < 1:
            return "error"

        req = requests.get(
            f"https://api.flutterwave.com/v3/banks/{country}",
            headers=self.get_flw_headers()
        )
        data = req.json()

        return data

    def transfer(
            self, bank: str, account_number: str,
            amount: int, narration: str, currency: str,
            reference: str, debit_currency: str, beneficiary_name=""
            ):

        body = {
            "account_bank": bank,
            "account_number": account_number,
            "amount": amount,
            "narration": narration,
            "currency": currency,
            "reference": reference,
            "debit_currency": debit_currency,
        }

        if beneficiary_name != "":
            body["beneficiary_name"] = beneficiary_name

        req = requests.post(
            url=self.get_transfer_url(),
            json=body,
            headers=self.get_flw_headers()
        )

        resp = req.json()

        return resp

    def transfer_bet9ja(self, amount: str, reference: str):
        resp = self.transfer(
            bank="flutterwave",
            account_number=os.getenv("BET9JA_MERCHANT_ID"),
            amount=amount,
            narration="Estrade-Tech Bet9ja Topup",
            reference=reference,
            currency="NGN",
            debit_currency="NGN"
        )
        return resp

    def fetch_transfer(self, id: str):
        url = self.get_transfer_url()+f"/{id}"
        req = requests.get(
            url=url,
            headers=self.get_flw_headers()
        )

        resp = req.json()
        status = resp.get("data").get("status")
        if status == "SUCCESSFUL":
            status = "success"
        return status

    def fetch_transaction(self, reference: str) -> dict:
        if reference == "invalid":
            return {
                'status': 'error',
                'message': 'Transaction not found',
                'data': None
            }
        req = requests.get(
            f"https://api.flutterwave.com/v3/bills/{reference}",
            headers=self.get_flw_headers()
        )
        data = req.json()

        if data.get('status') != 'success':
            return {
                'status': 'missing',
                'message': 'Transaction not found',
                'data': None
            }
        return data

