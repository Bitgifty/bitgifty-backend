from rest_framework import serializers
from decimal import Decimal

from giftCards.models import GiftCardFee
from .models import (
    GiftCard, Redeem, Transaction, StellarTransaction,
    StellarGiftCard, RedeemStellar
)

from core.sochitel import (
    ProductTypeEnum,
    ProductCategoryEnum,
)

from django.core.validators import MinValueValidator


class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCardFee
        fields = "__all__"


class CreateBillPaymentSerializer(serializers.Serializer):
    bill_type = serializers.CharField()
    amount = serializers.IntegerField()
    customer = serializers.CharField()
    country = serializers.CharField()
    chain = serializers.CharField()
    email = serializers.EmailField(required=False)
    wallet_address = serializers.CharField()
    crypto_amount = serializers.FloatField()
    transaction_hash = serializers.CharField()
    timestamp = serializers.CharField(required=False)
    offset = serializers.CharField(required=False)

    class Meta:
        ref_name = 'create_bill_dap'


class CreateBillPaymentSerializerV2(serializers.Serializer):
    biller_code = serializers.CharField(required=False)
    item_code = serializers.CharField(required=False)
    bill_type = serializers.CharField()
    amount = serializers.IntegerField()
    customer = serializers.CharField()
    country = serializers.CharField()
    chain = serializers.CharField()
    email = serializers.EmailField(required=False)
    wallet_address = serializers.CharField()
    crypto_amount = serializers.FloatField()
    transaction_hash = serializers.CharField()
    timestamp = serializers.CharField()
    offset = serializers.CharField()
    data_package_id = serializers.CharField(required=False)
    short_code = serializers.CharField(required=False)
    account_number = serializers.CharField(required=False)

    class Meta:
        ref_name = 'create_bill_dap_v2'


class GiftCardSerializer(serializers.ModelSerializer):
    class Meta:
        ref_name = 'giftcard_dap'
        model = GiftCard
        fields = "__all__"


class RedeemSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=False)

    class Meta:
        ref_name = 'redeem_dap'
        model = Redeem
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        ref_name = "dapp_transaction"


class StellarTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StellarTransaction
        fields = "__all__"
        ref_name = "stellar_dapp_transaction"


class CreateDepositNotificationSerializer(serializers.Serializer):
    token = serializers.CharField(required=False)
    amount = serializers.IntegerField()
    crypto_amount = serializers.FloatField()
    chain = serializers.CharField(required=False)
    wallet_address = serializers.CharField(required=False)
    transaction_hash = serializers.CharField(required=False)
    account_holder = serializers.CharField(required=False)
    client_id = serializers.CharField(required=False)


class ValidateCustomerBetSerializer(serializers.Serializer):
    phone = serializers.CharField()
    client_id = serializers.CharField()


class CheckBetSerializer(serializers.Serializer):
    txid = serializers.CharField()


class TransferSerializer(serializers.Serializer):
    bank = serializers.CharField()
    account_number = serializers.CharField()
    amount = serializers.IntegerField()
    narration = serializers.CharField()
    currency = serializers.CharField()
    transaction_hash = serializers.CharField()
    email = serializers.CharField()
    wallet_address = serializers.CharField()
    country = serializers.CharField()
    fiat_currency = serializers.CharField()
    customer = serializers.CharField()
    crypto_amount = serializers.CharField()
    beneficiary_name = serializers.CharField()


class CreateStellarBillPaymentSerializer(serializers.Serializer):
    biller_code = serializers.CharField(required=False)
    item_code = serializers.CharField(required=False)
    bill_type = serializers.CharField()
    amount = serializers.IntegerField()
    customer = serializers.CharField()
    country = serializers.CharField()
    chain = serializers.CharField()
    wallet_address = serializers.CharField()
    crypto_amount = serializers.FloatField()
    transaction_hash = serializers.CharField()

    class Meta:
        ref_name = 'create_bill__stellar_dapp'


class StellarGiftCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = StellarGiftCard
        fields = "__all__"


class StellarRedeemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedeemStellar
        fields = "__all__"


class SochitelProductTypeSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class SochitelCategoryTypeSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class SochitelProductSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    product_type = SochitelProductTypeSerializer()
    product_category = SochitelCategoryTypeSerializer()
    price_type = serializers.CharField()
    price = serializers.CharField()


class SochitelOperatorSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    brand_id = serializers.CharField()
    product_type = SochitelProductTypeSerializer()
    currency = serializers.CharField()
    country = serializers.CharField()


class SochitelTransactionRequestSerializer(serializers.Serializer):
    operator = serializers.CharField(max_length=50)
    msisdn = serializers.CharField(
        max_length=20, required=False, allow_null=True)
    account_id = serializers.CharField(
        max_length=50, required=False, allow_null=True)
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    amount_operator = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    product_id = serializers.CharField(
        max_length=50, required=False, allow_null=True)
    user_reference = serializers.CharField(
        max_length=50, required=False, allow_null=True)
    product_type = serializers.ChoiceField(
        choices=[(pt.value, pt.name) for pt in ProductTypeEnum],
        required=False
    )
    product_category = serializers.ChoiceField(
        choices=[(pc.value, pc.name) for pc in ProductCategoryEnum],
        required=False
    )
    extra_parameters = serializers.DictField(
        child=serializers.CharField(),
        required=False,
        allow_null=True
    )

    def validate(self, data):
        """
        Check that either amount or amount_operator is provided but not both.
        Also validate msisdn/account_id based on product type.
        """
        amount = data.get('amount')
        amount_operator = data.get('amount_operator')
        msisdn = data.get('msisdn')
        account_id = data.get('account_id')
        product_type = data.get('product_type')

        if amount is not None and amount_operator is not None:
            raise serializers.ValidationError(
                "Only one of amount or amount_operator should be provided"
            )

        if amount is None and amount_operator is None:
            raise serializers.ValidationError(
                "Either amount or amount_operator must be provided"
            )

        # Validate based on product type
        if product_type:
            if product_type == ProductTypeEnum.MOBILE_TOP_UP.value:
                if not msisdn:
                    raise serializers.ValidationError(
                        "MSISDN is required for mobile top-up")
            elif product_type == ProductTypeEnum.BILL_PAYMENT.value:
                if not account_id:
                    raise serializers.ValidationError(
                        "Account ID is required for bill payment")

        return data
