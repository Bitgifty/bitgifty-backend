from rest_framework import serializers

from .models import GiftCard

class GiftCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCard
        fields = "__all__"
