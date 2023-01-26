from rest_framework import serializers
from accounts.serializers import CustomUserDetailSerializer
from .models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    owner = CustomUserDetailSerializer(read_only=True)
    class Meta:
        model = Wallet
        exclude = ("private_key", "xpub", "mnemonic")
        read_only_fields = ("address", "owner", "qrcode")
