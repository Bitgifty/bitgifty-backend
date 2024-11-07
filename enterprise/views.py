
from rest_framework import (
    generics, exceptions, response, views,
    serializers
)
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.authentication import TokenAuthentication
from dj_rest_auth.serializers import UserDetailsSerializer


from drf_yasg.renderers import OpenAPIRenderer, SwaggerUIRenderer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from giftCards.serializers import (
    GiftCardSerializerV2, GiftCardImageSerializer,
)
from giftCards.models import GiftCardV2, GiftCardImage
from wallets.models import VirtualAccount
from accounts.models import Account

from core import utils

from .models import Transaction
from .serializers import (
    ValidateCustomerSerializer,
    CreateBillPaymentSerializer,
    PaymentStatusSerializer,
    TransactionSerializer,
)

# Create your views here.


class ListGiftCard(generics.ListAPIView):
    """
    List giftcards created by current user
    """
    serializer_class = GiftCardSerializerV2
    authentication_classes = [TokenAuthentication, ]

    def get_queryset(self):
        virtual_accounts = VirtualAccount.objects.filter(
            owner=self.request.user
        )
        query = GiftCardV2.objects.filter(
            wallet__in=virtual_accounts
        )

        return query


class ListGiftCardImageAPIView(generics.ListAPIView):
    """
    List of images to use in giftcards
    """
    authentication_classes = [TokenAuthentication, ]
    serializer_class = GiftCardImageSerializer
    queryset = GiftCardImage.objects.filter(version=2)


class GiftCardImageDetailView(generics.RetrieveAPIView):
    """
    Image details
    """
    authentication_classes = [TokenAuthentication, ]
    serializer_class = GiftCardImageSerializer
    queryset = GiftCardImage.objects.all()


class CreateGiftCardAPIView(generics.CreateAPIView):
    """
    Create a giftcard
    """
    serializer_class = GiftCardSerializerV2
    queryset = GiftCardV2.objects.all()
    authentication_classes = [TokenAuthentication, ]

    def perform_create(self, serializer, **kwargs):
        current_user = self.request.user
        network = serializer.validated_data.get("currency")
        note = serializer.validated_data.get("note")
        sender_note = "Gift card created"
        if note:
            sender_note = note
        recipient_note = "Gift card created"
        
        if network == "naira":
            network = "VC__BITGIFTY_NAIRA"
        wallet = VirtualAccount.objects.get(
            owner=current_user, chain__iexact=network
        )
        kwargs['wallet'] = wallet
        try:
            kwargs['code'] = wallet.create_giftcard(
                serializer.validated_data.get("amount"),
                sender_note=sender_note,
                recipient_note=recipient_note,
                operation_type="enterprise",
            )
        except Exception as exception:
            raise serializers.ValidationError(exception)
        serializer.save(**kwargs)


class GetBillCategoriesAPIView(views.APIView):
    """
    Query supported bill categories by country.
    The Biller country. Expected values include: NG, GH, and ZM.
    """
    renderer_classes = [
        JSONRenderer, BrowsableAPIRenderer,
        OpenAPIRenderer, SwaggerUIRenderer
    ]

    country = openapi.Parameter(
        'country', openapi.IN_QUERY,
        description="example: NG, GH", type=openapi.TYPE_STRING)
    authentication_classes = [TokenAuthentication, ]
    response_schema_dict = {
        "200": openapi.Response(
            description="Htpp 200 description",
            examples={
                "status": "success",
                "message": "Categories fetched successfully",
                "data": [
                    {
                        "id": 1,
                        "name": "Airtime",
                        "code": "AIRTIME",
                        "description": "Airtime",
                        "country_code": "NG"
                    },
                    {
                        "id": 2,
                        "name": "Mobile Data Service",
                        "code": "MOBILEDATA",
                        "description": "Mobile Data Service",
                        "country_code": "NG"
                    },
                    {
                        "id": 3,
                        "name": "Cable Bill Payment",
                        "code": "CABLEBILLS",
                        "description": "Cable Bill Payment",
                        "country_code": "NG"
                    },
                    {
                        "id": 4,
                        "name": "Internet Service",
                        "code": "INTSERVICE",
                        "description": "Internet Service",
                        "country_code": "NG"
                    },
                    {
                        "id": 5,
                        "name": "Utility Bills",
                        "code": "UTILITYBILLS",
                        "description": "Utility Bills",
                        "country_code": "NG"
                    },
                    {
                        "id": 6,
                        "name": "Tax Payment",
                        "code": "TAX",
                        "description": "Tax Payment",
                        "country_code": "NG"
                    },
                    {
                        "id": 7,
                        "name": "Donations",
                        "code": "DONATIONS",
                        "description": "Donations",
                        "country_code": "NG"
                    },
                    {
                        "id": 8,
                        "name": "Transport and Logistics",
                        "code": "TRANSLOG",
                        "description": "Transport and Logistics",
                        "country_code": "NG"
                    },
                    {
                        "id": 9,
                        "name": "Dealer Payments",
                        "code": "DEALPAY",
                        "description": "Dealer Payments",
                        "country_code": "NG"
                    },
                    {
                        "id": 10,
                        "name": "Airtime",
                        "code": "AIRTIME",
                        "description": "Airtime",
                        "country_code": "GH"
                    },
                    {
                        "id": 11,
                        "name": "Mobile Money",
                        "code": "MOBILEMONEY",
                        "description": "Mobile Money",
                        "country_code": "GH"
                    },
                    {
                        "id": 12,
                        "name": "Airtime",
                        "code": "AIRTIME",
                        "description": "Airtime",
                        "country_code": "KE"
                    },
                    {
                        "id": 13,
                        "name": "Cable Bill Payment",
                        "code": "CABLEBILLS",
                        "description": "Cable Bill Payment",
                        "country_code": "KE"
                    },
                    {
                        "id": 14,
                        "name": "Utility Bills",
                        "code": "UTILITYBILLS",
                        "description": "Utility Bills",
                        "country_code": "KE"
                    },
                    {
                        "id": 15,
                        "name": "Mobile Money",
                        "code": "MOBILEMONEY",
                        "description": "Mobile Money",
                        "country_code": "ZM"
                    },
                    {
                        "id": 16,
                        "name": "Airtime",
                        "code": "Airtime",
                        "description": "Airtime",
                        "country_code": "ZM"
                    },
                    {
                        "id": 17,
                        "name": "Religious Institutions",
                        "code": "RELINST",
                        "description": "Religious Institutions",
                        "country_code": "NG"
                    },
                    {
                        "id": 18,
                        "name": "Schools & Professional Bodies",
                        "code": "SCHPB",
                        "description": "Schools & Professional Bodies",
                        "country_code": "NG"
                    }
                ]
            }
        ),

        "400": openapi.Response(
            description="Htpp 400 description",
            examples={
                "status": "error",
                "message": "Country not supported at this time",
                "data": None
            }
        ),
    }

    @swagger_auto_schema(
        manual_parameters=[country],
        responses=response_schema_dict
    )
    def get(self, country: str):
        flw_client = utils.FlutterWave()
        categories = flw_client.get_bill_categories(country=country)
        return response.Response(categories)


class GetBillInfo(views.APIView):
    """Retrieve bill details provided by billers."""
    renderer_classes = [
        JSONRenderer, BrowsableAPIRenderer,
        OpenAPIRenderer, SwaggerUIRenderer
    ]
    authentication_classes = [TokenAuthentication, ]
    country = openapi.Parameter(
        'country', openapi.IN_QUERY,
        description="example: NG, GH", type=openapi.TYPE_STRING)

    response_schema_dict = {
        "200": openapi.Response(
            description="Htpp 200 description",
            examples={
                "status": "success",
                "message": "Billers fetched successfully",
                "data": [
                    {
                        "id": 66,
                        "name": "DSTV",
                        "logo": None,
                        "description": "DSTV",
                        "short_name": "DSTV",
                        "biller_code": "BIL119",
                        "country_code": "NG"
                    },
                    {
                        "id": 67,
                        "name": "GOTV",
                        "logo": None,
                        "description": "GOTV",
                        "short_name": "GOTV",
                        "biller_code": "BIL120",
                        "country_code": "NG"
                    },
                    {
                        "id": 68,
                        "name": "DAARSAT Communications",
                        "logo": None,
                        "description": "DAARSAT Communications",
                        "short_name": "DAARSAT Communications",
                        "biller_code": "BIL123",
                        "country_code": "NG"
                    },
                    {
                        "id": 69,
                        "name": "DSTV BOX OFFICE",
                        "logo": None,
                        "description": "DSTV BOX OFFICE",
                        "short_name": "DSTV BOX OFFICE",
                        "biller_code": "BIL125",
                        "country_code": "NG"
                    },
                    {
                        "id": 70,
                        "name": "MyTV",
                        "logo": None,
                        "description": "MyTV",
                        "short_name": "MyTV",
                        "biller_code": "BIL128",
                        "country_code": "NG"
                    },
                    {
                        "id": 71,
                        "name": "HiTV",
                        "logo": None,
                        "description": "HiTV",
                        "short_name": "HiTV",
                        "biller_code": "BIL129",
                        "country_code": "NG"
                    },
                    {
                        "id": 91,
                        "name": "STARTIMES",
                        "logo": None,
                        "description": "STARTIMES",
                        "short_name": "STARTIMES",
                        "biller_code": "BIL123",
                        "country_code": "NG"
                    }
                ]
            }
        ),

        "400": openapi.Response(
            description="Htpp 400 description",
            examples={
                "status": "error",
                "message": "Invalid category code",
                "data": None
            }
        ),
    }

    @swagger_auto_schema(
        manual_parameters=[country],
        responses=response_schema_dict
    )
    def get(self, biller_code: str):
        flw_client = utils.FlutterWave()
        categories = flw_client.get_bill_info(biller_code=biller_code)
        return response.Response(categories)


class ValidateCustomerDetails(generics.CreateAPIView):
    """
    Validate your customer's information.
    Supported input include: meter number, smartcard number,
    internet account number, etc.
    """
    serializer_class = ValidateCustomerSerializer
    authentication_classes = [TokenAuthentication, ]
    response_schema_dict = {
        "200": openapi.Response(
            description="Htpp 200 description",
            examples={
                "status": "success",
                "message": "Item validated successfully",
                "data": {
                    "response_code": "00",
                    "address": None,
                    "response_message": "Successful",
                    "name": "Test DSTV Account",
                    "biller_code": "BIL119",
                    "customer": "0025401100",
                    "product_code": "CB141",
                    "email": None,
                    "fee": 0,
                    "maximum": 0,
                    "minimum": 0
                }
            }
        ),

        "400": openapi.Response(
            description="Htpp 400 description",
            examples={
                "status": "error",
                "data": None
            }
        ),
    }

    @swagger_auto_schema(
        responses=response_schema_dict
    )
    def post(self, request, *args, **kwargs):
        serializer = ValidateCustomerSerializer(self.request.data)

        if serializer.is_valid():
            item_code = serializer.validated_data['item_code']
            biller_code = serializer.validated_data['biller_code']
            customer = serializer.validated_data['customer']

            flw_client = utils.FlutterWave()

            resp = flw_client.validate_customer_details(
                item_code=item_code,
                biller_code=biller_code,
                customer=customer
            )

            return response.Response(resp)


class CreateBillTransaction(generics.CreateAPIView):
    """Initiate your bill payments."""
    serializer_class = CreateBillPaymentSerializer
    authentication_classes = [TokenAuthentication, ]
    response_schema_dict = {
        "200": openapi.Response(
            description="Htpp 200 description",
            examples={
                "status": "success",
                "message": "Bill payment successful",
                "data": {
                    "phone_number": "0025401100",
                    "amount": 1800,
                    "network": "DSTV Access",
                    "code": "200",
                    "tx_ref": "CF-FLYAPI-20240311124623867907",
                    "reference": "247891569224",
                    "batch_reference": None,
                    "recharge_token": None,
                    "fee": 100
                }
            }
        ),

        "400": openapi.Response(
            description="Htpp 400 description",
            examples={
                "status": "error",
                "data": None
            }
        ),
    }

    @swagger_auto_schema(
        responses=response_schema_dict
    )
    def post(self, request, *args, **kwargs):
        serializer = CreateBillPaymentSerializer(
            data=self.request.data
        )

        if serializer.is_valid():
            country = serializer.validated_data['country']
            customer = serializer.validated_data['customer']
            bill_type = serializer.validated_data['bill_type']
            amount = serializer.validated_data['amount']
            email = serializer.validated_data.get('email')
            biller_code = serializer.validated_data.get('biller_code')
            item_code = serializer.validated_data.get('item_code')

            try:
                flw_client = utils.FlutterWave()
                trans_body = flw_client.build_body(
                    country,
                    customer,
                    amount
                )
                resp, reference = flw_client.make_payment(
                    biller_code,
                    item_code,
                    trans_body
                )
            except Exception as exception:
                raise ValueError(exception)

            try:
                status = "pending"

                if "airtime" in bill_type.lower():
                    status = "success"
                elif "data" in bill_type.lower():
                    status = "success"

                transaction = Transaction(
                    amount=amount,
                    currency_type="crypto",
                    status=status,
                    transaction_type=f"{bill_type} enterprise",
                    email=email,
                    ref=reference,
                    customer=customer,
                    bill_type=bill_type,
                    item_code=item_code,
                    biller_code=biller_code,
                )
                transaction.save()
            except Exception:
                raise ValueError("Transaction failed to save")
            return response.Response(resp)
        else:
            raise exceptions.ValidationError(
                "You aren't passing in a value correctly"
            )


class GetPaymentStatus(generics.CreateAPIView):
    """Get the status of a bill purchase."""
    authentication_classes = [TokenAuthentication, ]
    serializer_class = PaymentStatusSerializer
    response_schema_dict = {
        "200": openapi.Response(
            description="Htpp 200 description",
            examples={
                "status": "success",
                "message": "Bill status fetch successful",
                "data": {
                    "currency": "NGN",
                    "customer_id": "07065657658",
                    "frequency": "One Time",
                    "amount": "11.0000",
                    "fee": 0,
                    "product": "AIRTIME",
                    "product_name": None,
                    "commission": 0,
                    "transaction_date": "2024-03-08T15:55:16.963Z",
                    "customer_reference": "d7a004b1-a581-4cd9",
                    "country": "NG",
                    "flw_ref": "BPUSSD1709913319189093",
                    "tx_ref": "CF-FLYAPI-20240308035516465263",
                    "batch_id": 3387836,
                    "extra": None,
                    "product_details": "FLY-API-NG-AIRTIME",
                    "status": "successful",
                    "code": "200"
                }
            }
        ),

        "400": openapi.Response(
            description="Htpp 400 description",
            examples={
                "status": "error",
                "message": "Transaction not found",
                "data": None
            }
        ),
    }

    @swagger_auto_schema(
        responses=response_schema_dict
    )
    def post(self, request, *args, **kwargs):
        serializer = ValidateCustomerSerializer(self.request.data)

        if serializer.is_valid():
            reference = serializer.validated_data['reference']

            flw_client = utils.FlutterWave()

            resp = flw_client.get_payment_status(
                reference=reference
            )

            return response.Response(resp)


class GetTransactionAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, ]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        query = Transaction.objects.filter(
            user=self.request.user
        )
        return query


class GetUser(views.APIView):
    serializer_class = UserDetailsSerializer

    def get(self, *kwargs):
        query = Account.objects.get(pk=self.request.user.pk)
        user = {
            "pk": query.pk,
            "username": query.username,
            "email": query.email
        }
        return response.Response(user)
