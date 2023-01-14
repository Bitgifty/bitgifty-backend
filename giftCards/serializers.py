from rest_framework import serializers

from .models import GiftCard

class GiftCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCard
        exclude = ["binance_code", ]
        read_only_fields = ["binance_code", "encrypted_code", "owner"]
