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
            "network", "wallet_from", 
            "phone", "amount"
        )
        read_only_fields = ("user",)


class BuyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DataPurchase
        fields = (
            "wallet_from",
            "phone", "data_plan",
        )
        read_only_fields = ("user",)


class BuyCableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CablePurchase
        fields = (
            "cable_plan",
            "iuc", "wallet_from",
        )
        read_only_fields = ("user",)


class BuyElectricitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ElectricityPurchase
        fields = (
            "amount", 
            "meter_type", "meter_number",
            "disco", "wallet_from",
        )
        read_only_fields = ("user",)
