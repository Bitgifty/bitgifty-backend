import os
import requests
import random


import environ
import qrcode

from pathlib import Path

from cryptography.fernet import Fernet
from binance.spot import Spot

from cloudinary.uploader import upload
from cloudinary.utils import cloudinary


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
            cloud_name = os.getenv("CLOUD_NAME"),
            api_key = os.getenv("API_KEY"),
            api_secret = os.getenv("API_SECRET"),
            secure = True
        )

    def encrypt_credentials(self, mnemonic: str = None, xpub: str= None, private_key: str = None) -> dict:
        """
        Encrypt wallet mnemonics and xpubs 
        """
        key = os.getos.getenv("ENC_KEY")
        fernet = Fernet(key)
        output = {}
        
        if mnemonic:
            output["Mnemonic"] = fernet.encrypt(mnemonic.encode())
        if xpub:
            output["Xpub"] = fernet.encrypt(xpub.encode())
        if private_key:
            output["private_key"] = fernet.encrypt(private_key.encode())
        return output

    def decrypt_crendentails(self, token: str) -> str:
        try:
            key = os.getos.getenv("ENC_KEY")
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

    def generate_bnb_wallet(self) -> dict:
        url = "https://api.tatum.io/v3/bnb/account"

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
        url = f"https://api.tatum.io/v3/{network}/account/balance/{address}?type=testnet"
        
        if network == "tron":
            url = f"https://api.tatum.io/v3/{network}/account/{address}?type=testnet"
        elif network == "bitcoin":
            url = f"https://api.tatum.io/v3/{network}/address/balance/{address}?type=testnet"
        elif network == "bnb":
            url = f"https://api.tatum.io/v3/{network}/account/{address}?type=testnet"
        

        headers = {"x-api-key": self.key}

        response = requests.get(url, headers=headers)

        data = response.json()
        return data

    def get_transactions(self, address: dict, network:str) -> dict:
        combined_output = {}

        tron = {
            "url": f"https://api.tatum.io/v3/tron/transaction/account/{address.get('tron')}?type=testnet"
        }

        bnb = {
            "url": f"https://api.tatum.io/v3/bnb/account/transaction/{address.get('bnb')}",
            "query": {
                "startTime": "100",
                "endTime": "1651831727871",
            }
        }

        bitcoin = {
            "url": f"https://api.tatum.io/v3/bitcoin/transaction/address/{address.get('bitcoin')}?type=testnet",
            "query": {
                "pageSize": "10"
            }
        }

        celo = {
            "url": f"https://api.tatum.io/v3/celo/account/transaction/{address.get('celo')}?type=testnet",
            "query": {
                "pageSize": "10"
            }
        }

        ethereum = {
            "url": f"https://api.tatum.io/v3/ethereum/account/transaction/{address.get('ethereum')}?type=testnet",
            "query": {
                "pageSize": "10"
            }
        }


        selected_network = {
            "bnb": bnb,
            "bitcoin": bitcoin,
            "celo": celo,
            "ethereum": ethereum,
            "tron": tron,
        }
        

        try:
            check_network = selected_network[network]
            url = check_network["url"]
            query = check_network.get("query")
        except Exception:
            check_network = "all"
        
        
        headers = {"x-api-key": self.key}

        if check_network == "all":
            for network in selected_network:
                response = requests.get(selected_network[network]["url"], headers=headers, params=selected_network[network].get("query"))
                output = response.json()
                combined_output[network] = output
            data = combined_output
        else:
            response = requests.get(url, headers=headers, params=query)
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

    def send_token(self, receiver_address:str, network: str, amount: str, private_key: str, address: str) -> dict:
        tron = {
            "payload": {
                "fromPrivateKey": private_key,
                "to": receiver_address,
                "amount": str(amount)
            },
            "url": "https://api.tatum.io/v3/tron/transaction?type=testnet"
        }

        tron_usdt = {
            "payload": {
                "fromPrivateKey": private_key,
                "to": receiver_address,
                "tokenAddress": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                "feeLimit": 0.01,
                "amount": str(amount)
            },
            "url": "https://api.tatum.io/v3/tron/trc20/transaction"
        }

        bnb = {
            "url": "https://api.tatum.io/v3/bnb/transaction",
            "payload": {
                "to": receiver_address,
                "currency": "BNB",
                "amount": str(amount),
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
                "amount": str(amount),
                "fromPrivateKey": private_key
            }
        }

        ethereum = {
            "url": "https://api.tatum.io/v3/ethereum/transaction",
            "payload": {
                "to": receiver_address,
                "amount": str(amount),
                "currency": "ETH",
                "fromPrivateKey": private_key
            }
        }


        selected_network = {
            "bnb": bnb,
            "bitcoin": bitcoin,
            "celo": celo,
            "ethereum": ethereum,
            "tron": tron,
            "tron_usdt": tron_usdt
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.key
        }

        url = selected_network[network]["url"]
        payload = selected_network[network]["payload"]

        response = requests.post(url, json=payload, headers=headers)

        data = response.json()
        if data.get('txId'):
            return data
        else:
            raise ValueError(data.get('cause'))

    def generate_code(self):
        code = random.randint(000000, 999999)
        return code

    def create_gift_card(self, private_key: str, amount: str, receiver_address: str, network: str, sender_address: str) -> dict:
        private_key = self.decrypt_crendentails(private_key)
        self.send_token(receiver_address, network, amount, private_key, sender_address)
        code = self.generate_code()
        return code

    def redeem_gift_card(self, code, private_key: str, amount: str, receiver_address: str, network: str, sender_address: str) -> dict:
        private_key = self.decrypt_crendentails(private_key)
        self.send_token(receiver_address, network, amount, private_key, sender_address)       
        return code

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
