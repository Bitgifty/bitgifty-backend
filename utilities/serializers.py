from rest_framework import serializers

from wallets.serializers import WalletNormSerializer

from . import models



class CableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cable
        fields = "__all__"


class CablePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CablePlan
        fields = "__all__"


class DataPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DataPlan
        fields = "__all__"


class DiscoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Disco
        fields = "__all__"


class NetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Network
        fields = "__all__"


class BuyAirtimeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AirtimePurchase
        fields = (
            "token_amount", "network", "wallet_from", 
            "phone", "amount", "token_amount"
        )
        read_only_fields = ("user",)


class BuyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DataPurchase
        fields = (
            "token_amount", "wallet_from",
            "phone", "data_plan",
        )
        read_only_fields = ("user",)


class BuyCableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CablePurchase
        fields = (
            "token_amount", "cable_plan",
            "iuc", "wallet_from",
        )
        read_only_fields = ("user",)


class BuyElectricitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ElectricityPurchase
        fields = (
            "token_amount", "amount", 
            "meter_type", "meter_number",
            "disco", "wallet_from",
        )
        read_only_fields = ("user",)
