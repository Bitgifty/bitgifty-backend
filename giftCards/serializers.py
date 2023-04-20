from rest_framework import serializers

from .models import GiftCard, Redeem

class GiftCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCard
        fields = "__all__"
        read_only_fields = ["code", "account"]


class RedeemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redeem
        fields = "__all__"
        read_only_fields = ["account",]