import requests
from pathlib import Path
import environ

from cryptography.fernet import Fernet
from binance.spot import Spot

import os

def env_init():
    env = environ.Env()
    BASE_DIR = Path(__file__).resolve().parent.parent
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
    return env

env = env_init()
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

    def encrypt_credentials(self, mnemonic: str, xpub: str, private_key: str) -> dict:
        """
        Encrypt wallet mnemonics and xpubs 
        """
        key = os.getenv("ENC_KEY")
        fernet = Fernet(key)
        output = {}
        output["Mnemonic"] = fernet.encrypt(mnemonic.encode())
        output["Xpub"] = fernet.encrypt(xpub.encode())
        output["private_key"] = fernet.encrypt(private_key.encode())
        return output

    def decrypt_crendentails(self, token: str) -> str:
        try:
            key = os.getenv("ENC_KEY")
            fernet = fernet = Fernet(key)
            output = fernet.decrypt(token)
        except Exception as exception:
            raise ValueError(exception)
        return output.decode()
    
    def generate_credentials(self, network: str) -> dict:
        url = f"https://api.tatum.io/v3/{network}/wallet?type=testnet"
        headers = {"x-api-key": self.key}
        response = requests.get(url, headers=headers)
        data = response.json()
        return data

    def generate_wallet(self, xpub: str, network: str) -> dict:
        index = 1
        url = f"https://api.tatum.io/v3/{network}/address/{xpub}/{index}?type=testnet"

        headers = {"x-api-key": self.key}

        response = requests.get(url, headers=headers)

        data = response.json()
        return data
    
    def get_wallet_info(self, address:str, network: str) -> dict:
        url = f"https://api.tatum.io/v3/{network}/account/{address}?type=testnet"

        headers = {"x-api-key": self.key}

        response = requests.get(url, headers=headers)

        data = response.json()
        return data

    def get_transactions(self, address:str, network:str) -> dict:
        url = f"https://api.tatum.io/v3/{network}/transaction/account/{address}?type=testnet"

        headers = {"x-api-key": self.key}

        response = requests.get(url, headers=headers)

        data = response.json()
        return data

    def generate_private_key(self, mnemonic: str, network:str) -> str:
        url = f"https://api.tatum.io/v3/{network}/wallet/priv"

        payload = {
            "index": 1,
            "mnemonic": mnemonic
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.key
        }

        response = requests.post(url, json=payload, headers=headers)

        data = response.json()
        return data["key"]

    def send_token(self, receiver_address:str, network: str, amount: str, private_key: str) -> dict:
        url = f"https://api.tatum.io/v3/{network}/transaction?type=testnet"

        payload = {
            "fromPrivateKey": private_key,
            "to": receiver_address,
            "amount": amount
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.key
        }

        response = requests.post(url, json=payload, headers=headers)

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

# client = Blockchain(key=env("TATUM_API_KEY"), bin_key=env("BIN_KEY"), bin_secret=env("BIN_SECRET"))
# print(client.send_token("TXdiUinn2ir1bkbkhkG7TGUxGhHPkzvaqH", "tron", "10", "602aa822d94192838a38fb9b7578b2005573ec56d5c489d97c83d6037d3565ed"))
