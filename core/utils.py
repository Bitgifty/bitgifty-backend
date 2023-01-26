import os
import requests


import environ
import qrcode

from pathlib import Path

from cryptography.fernet import Fernet
from binance.spot import Spot

from cloudinary.uploader import upload
from cloudinary.utils import cloudinary



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

    def init_cloudinary(self) -> cloudinary.config:
        return cloudinary.config(
            cloud_name = env("CLOUD_NAME"),
            api_key = env("API_KEY"),
            api_secret = env("API_SECRET"),
            secure = True
        )

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
            key = env("ENC_KEY")
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
        print(data)
        return data
    
    def get_wallet_info(self, address:str, network: str) -> dict:
        url = f"https://api.tatum.io/v3/{network}/account/balance/{address}?type=testnet"
        
        if network == "tron":
            url = f"https://api.tatum.io/v3/{network}/account/{address}?type=testnet"
        elif network == "bitcoin":
            url = f"https://api.tatum.io/v3/{network}/address/balance/{address}?type=testnet"

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

    def send_token(self, receiver_address:str, network: str, amount: str, private_key: str, address: str = None) -> dict:
        tron = {
            "payload": {
                "fromPrivateKey": private_key,
                "to": receiver_address,
                "amount": amount
            },
            "url": "https://api.tatum.io/v3/tron/transaction?type=testnet"
        }

        bsc = {
            "url": "https://api.tatum.io/v3/bsc/transaction",
            "payload": {
                "to": receiver_address,
                "currency": "BSC",
                "amount": amount,
                "fromPrivateKey": private_key
            }
        }

        bitcoin = {
            "url": "https://api.tatum.io/v3/bitcoin/transaction",
            "payload": {
                "fromAddress": [
                    {
                    "address": address,
                    "privateKey": private_key
                    }
                ],
                "to": [
                    {
                    "address": receiver_address,
                    "value": float(amount)
                    }
                ]
            }
        }

        celo = {
            "url": "https://api.tatum.io/v3/celo/transaction",
            "payload": {
                "to": receiver_address,
                "currency": "CELO",
                "feeCurrency": "CELO",
                "amount": amount,
                "fromPrivateKey": private_key
            }
        }

        ethereum = {
            "url": "https://api.tatum.io/v3/ethereum/transaction",
            "payload": {
                "to": receiver_address,
                "amount": amount,
                "currency": "ETH",
                "fromPrivateKey": private_key
            }
        }


        selected_network = {
            "bnb": bsc,
            "bitcoin": bitcoin,
            "celo": celo,
            "ethereum": ethereum,
            "tron": tron,
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.key
        }

        url = selected_network[network]["url"]
        payload = selected_network[network]["payload"]

        response = requests.post(url, json=payload, headers=headers)

        data = response.json()
        return data

    def send_bsc(self, receiver_address:str, network: str, amount: str, private_key: str) -> dict:
        url = "https://api.tatum.io/v3/bsc/transaction"

        payload = {
        "to": "0x687422eEA2cB73B5d3e242bA5456b782919AFc85",
        "currency": "BSC",
        "amount": "100000",
        "fromPrivateKey": "0x05e150c73f1920ec14caa1e0b6aa09940899678051a78542840c2668ce5080c2"
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

    def create_qrcode(self, address: str) -> dict:
        qrcode_img = qrcode.make(address)
        qrcode_img.save(f'{address}.png')
        
    def upload_qrcode(self, address, email):
        self.init_cloudinary()
        self.create_qrcode(address)
        upload(f'{address}.png', use_filename=True, unique_filename=False, public_id=f'{address}', folder=f'qr_code/{email}')
        
        try:
            os.remove(f'{address}.png')
        except Exception as exception:
            raise ValueError({"error": str(exception)})

# client = Blockchain(key=env("TATUM_API_KEY"), bin_key=env("BIN_KEY"), bin_secret=env("BIN_SECRET"))
# print(client.send_token("TXdiUinn2ir1bkbkhkG7TGUxGhHPkzvaqH", "tron", "10", "602aa822d94192838a38fb9b7578b2005573ec56d5c489d97c83d6037d3565ed"))

# print(client.upload_qrcode('test'))