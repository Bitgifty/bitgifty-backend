import os
import json
import math
import requests
import secrets
import time

import qrcode

from cryptography.fernet import Fernet
from binance.spot import Spot

from cloudinary.uploader import upload
from cloudinary.utils import cloudinary



def get_rate(coin):
    # Opening JSON file
    f = open('price.json')
    
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    
    # Iterating through the json
    # list
    res = data[coin]
    
    # Closing file
    f.close()
    return float(res)

def get_naira_price():
    req = requests.get("https://api.remitano.com/api/v1/rates/ads")
    data = req.json()
    result = data["ng"]["usdt_bid"]
    return float(result)

class Blockchain(object):
    def __init__(
            self, key: str, bin_key: str = None,
            bin_secret: str=None,
            utility_url="https://arktivesub.com/api/data"
        ) -> None:
        self.key = key
        self.bin_key = bin_key
        self.bin_secret = bin_secret
        self.utility_url = utility_url

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
        key = os.getenv("ENC_KEY")
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
            key = os.getenv("ENC_KEY")
            fernet = fernet = Fernet(key)
            output = fernet.decrypt(token)
        except Exception as exception:
            raise ValueError(exception)
        return output.decode()
    
    def generate_credentials(self, network: str) -> dict:
        url = f"https://api.tatum.io/v3/{network}/wallet/"
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
        url = f"https://api.tatum.io/v3/{network}/address/{xpub}/{index}/"

        headers = {"x-api-key": self.key}

        response = requests.get(url, headers=headers)

        data = response.json()
        return data
    
    def get_wallet_info(self, address:str, network: str) -> dict:
        url = f"https://api.tatum.io/v3/{network}/account/balance/{address}/"
        
        if network == "tron":
            url = f"https://api.tatum.io/v3/{network}/account/{address}/"
        elif network == "bitcoin":
            url = f"https://api.tatum.io/v3/{network}/address/balance/{address}/"
        elif network == "bnb":
            url = f"https://api.tatum.io/v3/{network}/account/{address}/"
        

        headers = {"x-api-key": self.key}

        response = requests.get(url, headers=headers)

        data = response.json()
        return data

    def get_transactions(self, address: dict, network:str) -> dict:
        combined_output = {}

        tron = {
            "url": f"https://api.tatum.io/v3/tron/transaction/account/{address.get('tron')}/"
        }

        bnb = {
            "url": f"https://api.tatum.io/v3/bnb/account/transaction/{address.get('bnb')}",
            "query": {
                "startTime": "100",
                "endTime": "1651831727871",
            }
        }

        bitcoin = {
            "url": f"https://api.tatum.io/v3/bitcoin/transaction/address/{address.get('bitcoin')}/",
            "query": {
                "pageSize": "10"
            }
        }

        celo = {
            "url": f"https://api.tatum.io/v3/celo/account/transaction/{address.get('celo')}/",
            "query": {
                "pageSize": "10"
            }
        }

        ethereum = {
            "url": f"https://api.tatum.io/v3/ethereum/account/transaction/{address.get('ethereum')}/",
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
                response = requests.get(
                    selected_network[network]["url"],
                    headers=headers,
                    params=selected_network[network].get("query")
                )
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
            "url": "https://api.tatum.io/v3/tron/transaction/"
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
            raise ValueError(data)

    def generate_code(self):
        code = secrets.token_hex(16)
        return code

    def create_gift_card(
            self, private_key: str, amount: str,
            receiver_address: str, network: str, sender_address: str
        ) -> str:
        private_key = self.decrypt_crendentails(private_key)
        self.send_token(receiver_address, network, amount, private_key, sender_address)
        code = self.generate_code()
        return code

    def redeem_gift_card(
            self, code, private_key: str, amount: str,
            receiver_address: str, network: str, sender_address: str
        ) -> dict:
        private_key = self.decrypt_crendentails(private_key)
        self.send_token(
            receiver_address, network, amount, private_key, sender_address)       
        return code

    def create_qrcode(self, address: str) -> str:
        qrcode_img = qrcode.make(address)
        qrcode_img.save(f'{address}.png')
        return "success"
        
    def upload_qrcode(self, address, email):
        self.init_cloudinary()
        self.create_qrcode(address)
        upload(f'{address}.png', use_filename=True, unique_filename=False, public_id=f'{address}', folder=f'qr_code/{email}')
        
        try:
            os.remove(f'{address}.png')
        except Exception as exception:
            raise ValueError(str(exception))

    def initiate_swap(self, swap_from, swap_to, swap_amount, factor, usdt_price):
        try:
            swap_from.deduct(swap_amount)
            amount = math.floor(float(factor) * float(usdt_price) * float(swap_amount))
            swap_to.deposit(float(amount))
        except Exception as exception:
            raise ValueError(exception)
        return "success"

    def get_data_plans(self):
        plans = {
            "MTN": {
                "1.0GB": {
                    "network_id": 1,
                    "plan_name": "1.0GB",
                    "plan_id": 1,
                    "plan_type": "SME",
                    "amount": 220.00,
                    "validity": "1 month",
                },
                "3.0GB": {
                    "network_id": 1,
                    "plan_name": "3.0GB",
                    "plan_id": 2,
                    "plan_type": "SME",
                    "amount": 660.00,
                    "validity": "1 month",
                },
                "2.0GB": {
                    "network_id": 1,
                    "plan_name": "2.0GB",
                    "plan_id": 3,
                    "plan_type": "SME",
                    "amount": 440.00,
                    "validity": "1 month",
                },
                "5.0GB": {
                    "network_id": 1,
                    "plan_name": "5.0GB",
                    "plan_id": 4,
                    "plan_type": "SME",
                    "amount": 1100.00,
                    "validity": "1 month",
                },
                "10.0GB": {
                    "network_id": 1,
                    "plan_name": "10.0GB",
                    "plan_id": 5,
                    "plan_type": "SME",
                    "amount": 2200.00,
                    "validity": "1 month",
                },
                "500MB": {
                    "network_id": 1,
                    "plan_name": "500MB",
                    "plan_id": 6,
                    "plan_type": "SME",
                    "amount": 115,
                    "validity": "1 month",
                },
            },
            "AIRTEL": {
                "1.0GB": {
                    "network_id": 2,
                    "plan_name": "100MB",
                    "plan_id": 13,
                    "plan_type": "COOPERATE GIFTING",
                    "amount": 100.00,
                    "validity": "1 week",
                },
                "1.0GB": {
                    "network_id": 2,
                    "plan_name": "1.0GB",
                    "plan_id": 14,
                    "plan_type": "COOPERATE GIFTING",
                    "amount": 249.00,
                    "validity": "1 month",
                },
                "2.0GB": {
                    "network_id": 2,
                    "plan_name": "2.0GB",
                    "plan_id": 15,
                    "plan_type": "COOPERATE GIFTING",
                    "amount": 498.00,
                    "validity": "1 month",
                },
                "5.0GB": {
                    "network_id": 2,
                    "plan_name": "5.0GB",
                    "plan_id": 14,
                    "plan_type": "COOPERATE GIFTING",
                    "amount": 1245.00,
                    "validity": "1 month",
                },
            },
            "GLO": {
                "1.3GB": {
                    "network_id": 3,
                    "plan_name": "1.3GB",
                    "plan_id": 19,
                    "plan_type": "GIFTING",
                    "amount": 465.00,
                    "validity": "14 days",
                },
                "2.9GB": {
                    "network_id": 3,
                    "plan_name": "2.9GB",
                    "plan_id": 20,
                    "plan_type": "GIFTING",
                    "amount": 930.00,
                    "validity": "1 month",
                },
                "4.1GB": {
                    "network_id": 3,
                    "plan_name": "4.1GB",
                    "plan_id": 22,
                    "plan_type": "GIFTING",
                    "amount": 1450.00,
                    "validity": "1 month",
                },
                "5.8GB": {
                    "network_id": 3,
                    "plan_name": "5.8GB",
                    "plan_id": 21,
                    "plan_type": "GIFTING",
                    "amount": 1850.00,
                    "validity": "1 month",
                },
            },
            "9MOBILE": {
                "250MB": {
                    "network_id": 4,
                    "plan_name": "250MB",
                    "plan_id": 23,
                    "plan_type": "GIFTING",
                    "amount": 230.00,
                    "validity": "7 days",
                },
                "500MB": {
                    "network_id": 4,
                    "plan_name": "500MB",
                    "plan_id": 24,
                    "plan_type": "GIFTING",
                    "amount": 450.00,
                    "validity": "1 month",
                },
                "1.5GB": {
                    "network_id": 4,
                    "plan_name": "1.5GB",
                    "plan_id": 25,
                    "plan_type": "GIFTING",
                    "amount": 900.00,
                    "validity": "1 month",
                },
                "2GB": {
                    "network_id": 4,
                    "plan_name": "2GB",
                    "plan_id": 26,
                    "plan_type": "GIFTING",
                    "amount": 1070.00,
                    "validity": "1 month",
                },
                "3GB": {
                    "network_id": 4,
                    "plan_name": "3GB",
                    "plan_id": 27,
                    "plan_type": "GIFTING",
                    "amount": 1310.00,
                    "validity": "1 month",
                },
                "4.5GB": {
                    "network_id": 4,
                    "plan_name": "4.5GB",
                    "plan_id": 30,
                    "plan_type": "GIFTING",
                    "amount": 1750.00,
                    "validity": "1 month",
                },
            }   
        }
        return plans

    def get_data_plan(self, network: str, plan: str) -> float:
        plans = {
            "MTN": {
                "1.0GB": {
                    "network_id": 1,
                    "plan_name": "1.0GB",
                    "plan_id": 1,
                    "plan_type": "SME",
                    "amount": 220.00,
                    "validity": "1 month",
                },
                "3.0GB": {
                    "network_id": 1,
                    "plan_name": "3.0GB",
                    "plan_id": 2,
                    "plan_type": "SME",
                    "amount": 660.00,
                    "validity": "1 month",
                },
                "2.0GB": {
                    "network_id": 1,
                    "plan_name": "2.0GB",
                    "plan_id": 3,
                    "plan_type": "SME",
                    "amount": 440.00,
                    "validity": "1 month",
                },
                "5.0GB": {
                    "network_id": 1,
                    "plan_name": "5.0GB",
                    "plan_id": 4,
                    "plan_type": "SME",
                    "amount": 1100.00,
                    "validity": "1 month",
                },
                "10.0GB": {
                    "network_id": 1,
                    "plan_name": "10.0GB",
                    "plan_id": 5,
                    "plan_type": "SME",
                    "amount": 2200.00,
                    "validity": "1 month",
                },
                "500MB": {
                    "network_id": 1,
                    "plan_name": "500MB",
                    "plan_id": 6,
                    "plan_type": "SME",
                    "amount": 115,
                    "validity": "1 month",
                },
            },
            "AIRTEL": {
                "1.0GB": {
                    "network_id": 2,
                    "plan_name": "100MB",
                    "plan_id": 13,
                    "plan_type": "COOPERATE GIFTING",
                    "amount": 100.00,
                    "validity": "1 week",
                },
                "1.0GB": {
                    "network_id": 2,
                    "plan_name": "1.0GB",
                    "plan_id": 14,
                    "plan_type": "COOPERATE GIFTING",
                    "amount": 249.00,
                    "validity": "1 month",
                },
                "2.0GB": {
                    "network_id": 2,
                    "plan_name": "2.0GB",
                    "plan_id": 15,
                    "plan_type": "COOPERATE GIFTING",
                    "amount": 498.00,
                    "validity": "1 month",
                },
                "5.0GB": {
                    "network_id": 2,
                    "plan_name": "5.0GB",
                    "plan_id": 14,
                    "plan_type": "COOPERATE GIFTING",
                    "amount": 1245.00,
                    "validity": "1 month",
                },
            },
            "GLO": {
                "1.3GB": {
                    "network_id": 3,
                    "plan_name": "1.3GB",
                    "plan_id": 19,
                    "plan_type": "GIFTING",
                    "amount": 465.00,
                    "validity": "14 days",
                },
                "2.9GB": {
                    "network_id": 3,
                    "plan_name": "2.9GB",
                    "plan_id": 20,
                    "plan_type": "GIFTING",
                    "amount": 930.00,
                    "validity": "1 month",
                },
                "4.1GB": {
                    "network_id": 3,
                    "plan_name": "4.1GB",
                    "plan_id": 22,
                    "plan_type": "GIFTING",
                    "amount": 1450.00,
                    "validity": "1 month",
                },
                "5.8GB": {
                    "network_id": 3,
                    "plan_name": "5.8GB",
                    "plan_id": 21,
                    "plan_type": "GIFTING",
                    "amount": 1850.00,
                    "validity": "1 month",
                },
            },
            "9MOBILE": {
                "250MB": {
                    "network_id": 4,
                    "plan_name": "250MB",
                    "plan_id": 23,
                    "plan_type": "GIFTING",
                    "amount": 230.00,
                    "validity": "7 days",
                },
                "500MB": {
                    "network_id": 4,
                    "plan_name": "500MB",
                    "plan_id": 24,
                    "plan_type": "GIFTING",
                    "amount": 450.00,
                    "validity": "1 month",
                },
                "1.5GB": {
                    "network_id": 4,
                    "plan_name": "1.5GB",
                    "plan_id": 25,
                    "plan_type": "GIFTING",
                    "amount": 900.00,
                    "validity": "1 month",
                },
                "2GB": {
                    "network_id": 4,
                    "plan_name": "2GB",
                    "plan_id": 26,
                    "plan_type": "GIFTING",
                    "amount": 1070.00,
                    "validity": "1 month",
                },
                "3GB": {
                    "network_id": 4,
                    "plan_name": "3GB",
                    "plan_id": 27,
                    "plan_type": "GIFTING",
                    "amount": 1310.00,
                    "validity": "1 month",
                },
                "4.5GB": {
                    "network_id": 4,
                    "plan_name": "4.5GB",
                    "plan_id": 30,
                    "plan_type": "GIFTING",
                    "amount": 1750.00,
                    "validity": "1 month",
                },
            }   
        }
        return plans[network][plan]["plan_id"]

    def purchase_data(self, network: str, plan: int, phone: int):
        key = os.getenv("ARKTIVESUB_KEY")
        
        headers = {
            "Authorization": f"Token {key}",
            "Content-Type": "application/json"
        }

        request_id = f"Data_{plan}_{time.time()}"
        
        data = {
            "network": str(network),
            "phone": phone,
            "data_plan": str(plan),
            "bypass": False,
            "request-id": request_id
        }

        req = requests.post(
            url=self.utility_url,
            json=data,
            headers=headers
        )
        response = req.json()
        if response["status"] == "fail":
            raise ValueError(response["message"])
        return "success"
    
    def purchase_airtime(self, network: str, phone: str, amount: int) -> dict:
        network_id = {
            "MTN": 1,
            "AIRTEL": 2,
            "GLO": 3,
            "9MOBILE": 4
        }

        key = os.getenv("ARKTIVESUB_KEY")
        
        headers = {
            "Authorization": f"Token {key}",
            "Content-Type": "application/json"
        }

        request_id = f"Airtime_{network}_{amount}_{time.time()}"
        return
        data = {
            "network": network_id[network.upper()],
            "phone": phone,
            "plan_type": "VTU",
            "bypass": False,
            "amount": amount,
            "request-id": request_id
        }

        req = requests.post(
            url="https://arktivesub.com/api/topup/",
            headers=headers,
            json=data,
        )

        response = req.json()

        if not response.get("status"):
            raise ValueError("error purchasing airtime")
    
        if response["status"] == "fail":
            raise ValueError(response["message"])
        return response
    
    def purchase_electricity(
            self, disco: str, meter_type: str,
            meter_number: str, amount: int,
        ):

        key = os.getenv("ARKTIVESUB_KEY")
        
        headers = {
            "Authorization": f"Token {key}",
            "Content-Type": "application/json"
        }

        request_id = f"Bill_{disco}_{amount}_{time.time()}"

        data = {
            "disco": disco,
            "meter_type": meter_type,
            "meter_number": meter_number,
            "amount": amount,
            "bypass": False,
            "request_id": request_id
        }
    
        req = requests.post(
            url="https://arktivesub.com/api/bill",
            headers=headers,
            json=data,
        )
        response = req.json()
        return response

    def purchase_cable(self, cable: int, iuc: str, plan: int) -> dict:
        
        url = "https://arktivesub.com/api/cable"

        request_id = f"Cable_{iuc}_{time.time()}"

        data = {
            "cable": cable,
            "iuc": iuc,
            "cable_plan": plan,
            "bypass": False,
            "request_id": request_id
        }
        
        key = os.getenv("ARKTIVESUB_KEY")
        
        headers = {
            "Authorization": f"Token {key}",
            "Content-Type": "application/json"
        }
    
        req = requests.post(
            url=url,
            json=data,
            headers=headers
        )

        response = req.json()

        return response

    def buy_data(self, wallet, amount, network, phone, plan, token_amount):
        try:
            self.purchase_data(network, plan, phone)
            wallet.deduct(token_amount)
        except Exception as exception:
            raise ValueError(exception)
        return "success"

    def buy_airtime(self, wallet, network, phone, amount, token_amount) -> str:
        try:
            self.purchase_airtime(network, phone, amount)
            wallet.deduct(token_amount)
        except Exception as exception:
            raise ValueError(exception)
        return "success"

    def buy_electricity(self, wallet, disco, meter_type, meter_number, amount, token_amount) -> str:
        try:
            self.purchase_electricity(disco, meter_type, meter_number, amount)
            wallet.deduct(token_amount)
        except Exception as exception:
            raise ValueError(exception)
        return "success"

    def buy_cable(self, wallet, cable, iuc, plan, amount) -> str:
        try:
            self.purchase_cable(cable, iuc, plan)
            wallet.deduct(amount)
        except Exception as exception:
            raise ValueError(exception)
        return "success"
