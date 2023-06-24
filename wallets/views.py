import os

from django.shortcuts import render

from django.http import HttpResponse

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .serializers import WalletSerializer
from .models import Wallet

from accounts.models import Account
from core.utils import Blockchain
# Create your views here.


class WalletAPIView(generics.GenericAPIView):
    serializer_class = WalletSerializer
    
    def get_queryset(self):
        current_user = self.request.user
        wallet = Wallet.objects.filter(owner=current_user)
        return wallet

    def get(self, request):
        wallet_list = {}
        try:
            network_mapping = {
                "bnb": "bnb",
                "bitcoin": "bitcoin",
                "celo": "celo",
                "ethereum": "ethereum",
                "tron": "tron"
            }
            user = request.user
            wallets = Wallet.objects.filter(owner=user)

            for wallet in wallets:
                network_key = wallet.network.lower()
                network = network_mapping[network_key]
                client = Blockchain(os.getenv("TATUM_API_KEY"), os.getenv("BIN_KEY"), os.getenv("BIN_SECRET"))
                wallet_info = client.get_wallet_info(wallet.address, network)
                
                wallet_list[wallet.network] = {
                    'address': wallet.address,
                    'info': wallet_info,
                    'qrcode': wallet.qrcode,
                }
            return Response(wallet_list, status=status.HTTP_200_OK)
        except Exception as exception:
            raise ValidationError({"error": exception})


def recreate_wallet(request):
    TATUM_API_KEY = os.getenv("TATUM_API_KEY")
    client = Blockchain(key=TATUM_API_KEY)
    
    cloud_name = os.getenv("CLOUD_NAME")
    network_mapping = {
        "bnb": "bnb",
        "bitcoin": "bitcoin",
    }
    accounts = Account.objects.all()
    for account in accounts:
        for key in network_mapping:
            if key == "bnb":
                credentials = client.generate_bnb_wallet()
                wallet_address = credentials["address"]
                private_key = credentials["privateKey"]
                encrypted_credentials = client.encrypt_credentials(
                    private_key=private_key
                )
                private_enc = encrypted_credentials["private_key"]
                xpub_enc = None
                mnemonic_enc = None
                try:
                    old = Wallet.objects.get(owner=account, network=key.title())
                    old.delete()
                except Exception:
                    pass
            else:
                credentials = client.generate_credentials(network_mapping[key])
                wallet = client.generate_wallet(credentials["xpub"], network_mapping[key])
                private_key = client.generate_private_key(credentials["mnemonic"], network_mapping[key])
            
                encrypted_credentials = client.encrypt_credentials(
                credentials["mnemonic"], credentials["xpub"], private_key
                )
                wallet_address = wallet["address"]
                
                xpub_enc = encrypted_credentials["Xpub"]
                mnemonic_enc = encrypted_credentials["Mnemonic"]
                private_enc = encrypted_credentials["private_key"]
                client.upload_qrcode(wallet_address, account.email)
                try:
                    old = Wallet.objects.get(owner=account, network=key.title())
                    old.delete()
                except Exception:
                    pass
            if xpub_enc and mnemonic_enc:
                user_wallet = Wallet(
                    owner=account,
                    address=wallet_address,
                    private_key=private_enc.decode(),
                    xpub=xpub_enc.decode(),
                    mnemonic=mnemonic_enc.decode(),
                    network=key.title(),
                    qrcode=f'https://res.cloudinary.com/{cloud_name}/image/upload/qr_code/{account.email}/{wallet_address}.png'
                )
            else:
                user_wallet = Wallet(
                    owner=account,
                    address=wallet_address,
                    private_key=private_enc.decode(),
                    network=key.title(),
                    qrcode=f'https://res.cloudinary.com/{cloud_name}/image/upload/qr_code/{account.email}/{wallet_address}.png'
                )
            user_wallet.save()
    return HttpResponse("success")
