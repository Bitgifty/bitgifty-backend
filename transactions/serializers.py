from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class TransactionConfirmSerializer(serializers.Serializer):
    transaction_hash = serializers.CharField()
    transaction_chain = serializers.CharField()


class WithdrawalSerializer(serializers.Serializer):
    amount = serializers.CharField()
    receiver_address = serializers.CharField(required=False)
    network = serializers.CharField(required=False)
    transaction_type = serializers.CharField(required=False)
