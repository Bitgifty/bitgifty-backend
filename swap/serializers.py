from rest_framework import serializers

from wallets.models import Wallet
from .models import Swap, SwapTable


class SwapSerializer(serializers.Serializer):
    swap_from = serializers.CharField()
    swap_to = serializers.CharField()
    swap_amount = serializers.CharField()
    current_user = serializers.SerializerMethodField('_user')

    def _user(self):
        request = self.context.get('request', None)
        if request:
            return request.user

    def save(self):
        try:
            swap_from = Wallet.objects.get(owner=self._user, network=self.swap_from)
        except Wallet.DoesNotExist:
            raise serializers.ValidationError({"error": "Exchange not supported"})
        
        try:
            swap_to = Wallet.objects.get(owner=self._user, network=self.swap_to)
        except Wallet.DoesNotExist:
            raise serializers.ValidationError({"error": "Exchange not supported"})
        
        swap_table = SwapTable.objects.get(buy=self.swap_from, using=self.swap_to)

        swap = Swap(
            swap_from,
            swap_to,
            self.swap_amount,
            swap_table
            )
        swap.save()
