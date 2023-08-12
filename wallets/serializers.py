from rest_framework import serializers
from accounts.serializers import CustomUserDetailSerializer
from .models import Wallet


class WalletNormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ("pk",)

class WalletSerializer(serializers.ModelSerializer):
    owner = CustomUserDetailSerializer(read_only=True)
    class Meta:
        model = Wallet
        exclude = ("private_key", "xpub", "mnemonic")
        read_only_fields = ("address", "owner", "qrcode")


class WalletUpdateSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(source='address')

    class Meta:
        model = Wallet
        read_only_fields = ("qrcode", "balance")
        exclude = ("private_key", "xpub", "mnemonic", "address", "owner", "network")
