import requests

from cryptography.fernet import Fernet
from binance.spot import Spot

import os

class Blockchain(object):
    def __init__(self, key: str, bin_key: str = None, bin_secret: str=None) -> None:
        self.key = key
        self.bin_key = bin_key
        self.bin_secret = bin_secret

    def init_binance(self) -> Spot:
        """
        Generate a new binance client for making requests to binance API
        """
        client = Spot(self.bin_key, self.bin_secret)
        return client

    def encrypt_credentials(self, mnemonic: str, xpub: str) -> dict:
        """
        Encrypt wallet mnemonics and xpubs 
        """
        fernet = Fernet(os.getenv("ENC_KEY"))
        output = {}
        output["Mnemonic"] = fernet.encrypt(mnemonic.encode())
        output["Xpub"] = fernet.encrypt(xpub.encode())
        return output

    def decrypt_crendentails(self, token: str) -> dict:
        fernet = fernet = Fernet(os.getenv("ENC_KEY"))
        output = fernet.decrypt(token)
        return output
    
    def generate_credentials(self, network: str) -> dict:
        url = f"https://api.tatum.io/v3/{network}/wallet"
        headers = {"x-api-key": self.key}
        response = requests.get(url, headers=headers)
        data = response.json()
        return data

    def generate_wallet(self, xpub: str, network: str) -> dict:
        index = 1
        url = f"https://api.tatum.io/v3/{network}/address/{xpub}/{index}"

        headers = {"x-api-key": self.key}

        response = requests.get(url, headers=headers)

        data = response.json()
        return data
    
    def get_wallet_info(self, address:str, network: str) -> dict:
        url = f"https://api.tatum.io/v3/{network}/account/" + address

        headers = {"x-api-key": self.key}

        response = requests.get(url, headers=headers)

        data = response.json()
        return data

    def get_transactions(self, address:str, network:str) -> dict:
        url = "https://api.tatum.io/v3/tron/transaction/account/" + address

        headers = {"x-api-key": self.key}

        response = requests.get(url, headers=headers)

        data = response.json()
        return data

    def create_gift_card(self, token: str, amount: str) -> dict:
        client = self.init_binance()
        response = client.gift_card_create_code(token, amount)
        return response

    def reedem_gift_card(self, code: str) -> dict:
        client = self.init_binance()
        response = client.gift_card_redeem_code(code)
        return response

# client = Blockchain(key=os.getenv("TATUM_API_KEY"))
# credentials = client.generate_credentials("tron")

# print("credentials: ", credentials)

# xpub = credentials["xpub"]

# print("xpub: ", xpub)
# mnemonics = credentials["mnemonic"]

# print("mnemonics: ", mnemonics)

# wallet = client.generate_wallet(xpub)

# print("wallet: ", wallet)
