from rest_framework import serializers
from .models import Transaction


class CategorySerializer(serializers.Serializer):
    id = serializers.CharField(default=1)
    name = serializers.CharField(default="Airtime",)
    code = serializers.CharField(default="AIRTIME",)
    description = serializers.CharField(default="Airtime",)
    country_code = serializers.CharField(default="NG")

    class Meta:
        ref_name = "enterprise_validate_customer_serializer"
        

class BillCategorySerializer(serializers.Serializer):
    status = serializers.CharField(default="success")
    message = serializers.CharField(
        default="Categories fetched successfully"
    )
    # data = CategorySerializer(many=True, read_only=True)
    # data = serializers.ListField(child=CategorySerializer())

    class Meta:
        fields = "__all__"
        ref_name = "enterprise_bill_category_serializer"


class ValidateCustomerSerializer(serializers.Serializer):
    item_code = serializers.CharField(required=True)
    biller_code = serializers.CharField(required=False)
    customer = serializers.CharField(required=True)

    class Meta:
        ref_name = "enterprise_validate_customer_serializer"


class PaymentStatusSerializer(serializers.Serializer):
    reference = serializers.CharField(required=True)
    
    class Meta:
        ref_name = "enterprise_payment_status_serializer"


class CreateBillPaymentSerializer(serializers.Serializer):
    bill_type = serializers.CharField(help_text="eg. MOBILEDATA")
    amount = serializers.IntegerField(help_text="lowest is 100")
    customer = serializers.CharField(
        help_text="can be phone number, IUC number or meter number"
    )
    country = serializers.CharField(help_text="eg. NG, GH")
    email = serializers.EmailField(required=False)
    biller_code = serializers.EmailField(help_text="eg. BIL108")
    item_code = serializers.EmailField(help_text="eg. MD141")

    class Meta:
        ref_name = 'enterprise_create_bill_enterpise'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            "id", "amount", "currency", "status",
            "time", "email", "ref", "customer", "biller_code",
            "item_code", "bill_type", "country"
        )
        ref_name = "enterprise_transaction_serializer"
