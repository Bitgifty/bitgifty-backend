from rest_framework import serializers

from .models import GiftCard, Redeem

class GiftCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCard
        exclude = ["code", ]
        read_only_fields = ["code", "encrypted_code", "account"]


class RedeemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redeem
        read_only_fields = ["account",]