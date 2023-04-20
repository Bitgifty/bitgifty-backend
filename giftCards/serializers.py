from rest_framework import serializers

from .models import GiftCard, Redeem, GiftCardImage


class GiftCardImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCardImage
        fields = "__all__"

class GiftCardSerializer(serializers.ModelSerializer):
    image = GiftCardImageSerializer()
    class Meta:
        model = GiftCard
        fields = "__all__"
        read_only_fields = ["code", "account"]


class RedeemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redeem
        fields = "__all__"
        read_only_fields = ["account",]