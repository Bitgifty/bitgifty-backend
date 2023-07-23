from rest_framework import serializers

from wallets.models import Wallet
from .models import Swap, SwapTable


class SwapSerializer(serializers.Serializer):
    swap_from = serializers.CharField()
    swap_to = serializers.CharField()
    swap_amount = serializers.CharField()

    def save(self):
        swap_amount = self.validated_data["swap_amount"]
        _user = self.context['request'].user
        swap_from_string = self.validated_data["swap_from"]
        swap_to_string = self.validated_data["swap_to"]

        if swap_to_string != "naira":
            swap_to_string = swap_to_string.title()

        if swap_from_string != "naira":
            swap_from_string = swap_from_string.title()

        try:
            swap_from = Wallet.objects.get(
                owner=_user,
                network=swap_from_string
            )
        except Wallet.DoesNotExist:
            raise serializers.ValidationError(
                f"{swap_from} wallet doesn't exist"
            )
        
        try:
            swap_to = Wallet.objects.get(owner=_user, network="naira")
        except Wallet.DoesNotExist:
            raise serializers.ValidationError(
                f"{swap_to} wallet doesn't exist"
            )
        
        try:
            swap_table = SwapTable.objects.get(buy="naira", using=swap_from_string.lower())
        except SwapTable.DoesNotExist: 
            raise serializers.ValidationError(
                "Exchange not supported yet"
            )
        try:
            swap = Swap(
                swap_from=swap_from,
                swap_to=swap_to,
                swap_amount=swap_amount,
                swap_table=swap_table
                )
            swap.save()
        except Exception as exception:
            raise serializers.ValidationError(exception)

