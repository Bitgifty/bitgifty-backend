import os
import secrets
import requests
from typing import Dict, Any, List
from decimal import Decimal, InvalidOperation

from django.core import mail
from django.db.models import Q

from datetime import datetime

from .models import Transaction

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, exceptions, response, views, permissions
from rest_framework import filters, status
from rest_framework import serializers as rest_serializers

from django_filters.rest_framework import (
    DjangoFilterBackend, DateRangeFilter,
    FilterSet, DateFilter, AllValuesFilter
)

# from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
# from oauth2_provider.contrib.rest_framework import OAuth2Authentication

from core.utils import Blockchain, get_alt_flw_headers, get_naira_price
from core.pretium import Pretium
from core.bet9ja import Bet9ja
from core.stellar import Stellar
from core.flutterwave import FlutterWave
from core import sochitel

from giftCards.models import GiftCardFee
from wallets.models import AdminWallet

from core.sochitel import (
    ExecTransactionRequest, APIError
)

from . import serializers, models
# Create your views here.


class TransactionDateFilter(FilterSet):
    start_date = DateFilter(field_name='time', lookup_expr=('gt'),)
    end_date = DateFilter(field_name='time', lookup_expr=('lt'))
    date_range = DateRangeFilter(field_name='time')
    wallet_address = AllValuesFilter(field_name='wallet_address')
    currency = AllValuesFilter(field_name='currency')
    status = AllValuesFilter(field_name='status')
    transaction_type = AllValuesFilter(field_name='transaction_type')
    country = AllValuesFilter(field_name='country')
    bill_type = AllValuesFilter(field_name='bill_type')

    class Meta:
        model = models.Transaction
        fields = [
            'start_date', 'end_date', 'date_range',
            'wallet_address', 'currency', 'status',
            'transaction_type', 'country', 'bill_type'
        ]


class StellarTransactionDateFilter(FilterSet):
    start_date = DateFilter(field_name='time', lookup_expr=('gt'),)
    end_date = DateFilter(field_name='time', lookup_expr=('lt'))
    date_range = DateRangeFilter(field_name='time')
    wallet_address = AllValuesFilter(field_name='wallet_address')
    currency = AllValuesFilter(field_name='currency')
    status = AllValuesFilter(field_name='status')
    transaction_type = AllValuesFilter(field_name='transaction_type')
    country = AllValuesFilter(field_name='country')
    bill_type = AllValuesFilter(field_name='bill_type')

    class Meta:
        model = models.StellarTransaction
        fields = [
            'start_date', 'end_date', 'date_range',
            'wallet_address', 'currency', 'status',
            'transaction_type', 'country', 'bill_type'
        ]



class GetFeesAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny,]
    queryset = GiftCardFee.objects.all()
    serializer_class = serializers.FeeSerializer
    filterset_fields = ['network',]


class GetBillCategoriesAPIView(views.APIView):
    permission_classes = [permissions.AllowAny,]
    bill_type = openapi.Parameter(
        'bill-type', openapi.IN_QUERY,
        description="example: airtime, data_bundle", type=openapi.TYPE_STRING
    )
    provider = openapi.Parameter(
        'provider', openapi.IN_QUERY,
        description="example: MTN, GLO, Airtel, 9Mobile",
        type=openapi.TYPE_STRING
    )

    response_schema_dict = {
        "201": openapi.Response(
            description="Htpp 201 description",
            examples={
                "status": "success",
                "message": "bill categories retrieval successful",
                "data": [
                    {
                        "id": 1,
                        "biller_code": "BIL099",
                        "name": "MTN NIgeria",
                        "default_commission": 0.02,
                        "date_added": "2018-07-03T00:00:00Z",
                        "country": "NG",
                        "is_airtime": True,
                        "biller_name": "AIRTIME",
                        "item_code": "AT099",
                        "short_name": "MTN",
                        "fee": 0,
                        "commission_on_fee": False,
                        "label_name": "Mobile Number",
                        "amount": 0
                    },
                    {
                        "id": 2,
                        "biller_code": "BIL099",
                        "name": "GLO Nigeria",
                        "default_commission": 0.025,
                        "date_added": "2018-07-03T00:00:00Z",
                        "country": "NG",
                        "is_airtime": True,
                        "biller_name": "AIRTIME",
                        "item_code": "AT099",
                        "short_name": "GLO",
                        "fee": 0,
                        "commission_on_fee": False,
                        "label_name": "Mobile Number",
                        "amount": 0
                    },
                    {
                        "id": 9,
                        "biller_code": "BIL119",
                        "name": "DSTV BoxOffice",
                        "default_commission": 0.3,
                        "date_added": "2018-08-17T00:00:00Z",
                        "country": "NG",
                        "is_airtime": False,
                        "biller_name": "DSTV BOX OFFICE",
                        "item_code": "CB140",
                        "short_name": "Box Office",
                        "fee": 100,
                        "commission_on_fee": True,
                        "label_name": "Smart Card Number",
                        "amount": 0
                    },
                ]
            }
        ),

        "500": openapi.Response(
            description="Htpp 500 description",
            examples={
                "application/json": {
                    "key_1": "error message 1",
                    "key_2": "error message 2",
                }
            }
        ),
    }

    def make_request(self, bill_type: str, provider: str):
        biller_code = {
            "MTN": "BIL099",
            "GLO": "BIL102",
            "Airtel": "BIL100",
            "9Mobile": "BIL103",
        }

        params = {
            bill_type: 1
        }

        if provider:
            params["biller_code"] = biller_code[provider]

        r = requests.get(
            url="https://api.flutterwave.com/v3/bill-categories",
            params=params,
            headers=get_alt_flw_headers()
        )

        response = r.json()

        if response.get("status") != "success":
            raise ValueError("error getting bill category")
        return response

    @swagger_auto_schema(manual_parameters=[bill_type, provider], )
    def get(self, *args, **kwargs):
        bill_type = self.request.query_params.get('bill-type')
        provider = self.request.query_params.get('provider')

        res = self.make_request(bill_type, provider)
        return response.Response(res)


class GetBillCategoriesV2APIView(views.APIView):
    permission_classes = [permissions.AllowAny,]
    country = openapi.Parameter(
        'country', openapi.IN_QUERY,
        description="example: GH, KE, GH", type=openapi.TYPE_STRING)

    def make_request(self, country: str):

        params = {
            "country": country
        }

        r = requests.get(
            url="https://api.flutterwave.com/v3/top-bill-categories",
            params=params,
            headers=get_alt_flw_headers()
        )

        response = r.json()

        if response.get("status") != "success":
            raise ValueError("error getting bill category")
        return response

    @swagger_auto_schema(manual_parameters=[country], )
    def get(self, *args, **kwargs):
        country = self.request.query_params.get('country')

        res = self.make_request(country)
        return response.Response(res)


class GetBillerInfoAPIView(views.APIView):
    permission_classes = [permissions.AllowAny,]
    country = openapi.Parameter(
        'country', openapi.IN_QUERY,
        description="example: GH, KE, GH", type=openapi.TYPE_STRING)
    category = openapi.Parameter(
        'category', openapi.IN_QUERY,
        description="example: CABLEBILLS", type=openapi.TYPE_STRING)

    def get_biller_info(self, category: str, country: str):
        params = {
            "country": country
        }

        r = requests.get(
            url=f"https://api.flutterwave.com/v3/bills/{category}/billers",
            params=params,
            headers=get_alt_flw_headers()
        )

        response = r.json()
        if response.get("status") != "success":
            raise ValueError("error getting biller info")
        return response

    @swagger_auto_schema(manual_parameters=[country, category], )
    def get(self, *args, **kwargs):
        country = self.request.query_params.get('country')
        category = self.request.query_params.get('category')

        res = self.get_biller_info(category, country)
        return response.Response(res)


class GetBillInfoAPIView(views.APIView):
    permission_classes = [permissions.AllowAny,]
    biller_code = openapi.Parameter(
        'biller_code', openapi.IN_QUERY,
        description="example: BIL119", type=openapi.TYPE_STRING)

    def get_bill_info(self, biller_code: str):

        r = requests.get(
            url=f"https://api.flutterwave.com/v3/billers/{biller_code}/items",
            headers=get_alt_flw_headers()
        )

        response = r.json()

        if response.get("status") != "success":
            raise ValueError("error getting biller info")
        return response

    @swagger_auto_schema(manual_parameters=[biller_code], )
    def get(self, *args, **kwargs):
        biller_code = self.request.query_params.get('biller_code')

        res = self.get_bill_info(biller_code)
        return response.Response(res)


class ValidateBillServiceAPIView(views.APIView):
    permission_classes = [permissions.AllowAny,]
    item_code = openapi.Parameter(
        'item-code', openapi.IN_QUERY,
        description="get item code from get bill category",
        type=openapi.TYPE_STRING
    )
    biller_code = openapi.Parameter(
        'biller-code',
        openapi.IN_QUERY,
        description="get biller code from get bill category",
        type=openapi.TYPE_STRING
    )
    customer = openapi.Parameter(
        'customer',
        openapi.IN_QUERY,
        description="phone number, meter number or IUC number",
        type=openapi.TYPE_STRING
    )

    def validate_bill(self, item_code: str, biller_code: str, customer: str):
        url = "https://api.flutterwave.com/v3/bill-items/"\
            f"{item_code}/validate?code={biller_code}&&customer={customer}"
        req = requests.get(url=url, headers=get_alt_flw_headers())
        resp = req.json()
        return resp

    @swagger_auto_schema(
            manual_parameters=[item_code, biller_code, customer]
        )
    def get(self, *args, **kwargs):
        item_code = self.request.query_params.get('item-code')
        biller_code = self.request.query_params.get('biller-code')
        customer = self.request.query_params.get('customer')

        try:
            validate = self.validate_bill(item_code, biller_code, customer)
        except Exception as exception:
            raise ValueError(f"{exception}: while validating customer")
        return response.Response(validate)


class CreateBillPaymentV2APIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.CreateBillPaymentSerializerV2

    def save_sus_transaction(
            self, amount, chain, crypto_amount,
            bill_type, email="", wallet_address="",
            transaction_hash="", biller_code="",
            item_code="", short_code="",
            customer="", country=""
            ):
        reference = secrets.token_hex(7)
        transaction = models.Transaction(
            amount=amount,
            currency=chain,
            currency_type="crypto",
            crypto_amount=crypto_amount,
            status="failed",
            transaction_type=f"{bill_type} dapp",
            email=email,
            wallet_address=wallet_address,
            transaction_hash=transaction_hash,
            bill_type=bill_type,
            biller_code=biller_code,
            item_code=item_code,
            short_code=short_code,
            ref=f"sus-{reference}",
            customer=customer,
            country=country,
        )
        return transaction

    def initiate_payment(
            self, biller_code, item_code, country,
            customer, amount, bill_type="", data_package_id=0, short_code="",
            account_number=""
            ):

        if country == "KE" or country == "ZA" or country == "UG":
            pretium = Pretium(api_key=os.getenv("PRETIUM_KEY"))

            try:

                if bill_type == "AIRTIME":
                    resp, reference = pretium.buy_airtime(
                        amount, customer, country
                    )
                if bill_type == "MOBILEDATA":
                    resp, reference = pretium.buy_data(
                        amount, customer,
                        data_package_id
                    )
                if bill_type == "BUY_GOODS":
                    resp, reference = pretium.buy_goods(
                        amount, short_code=short_code,
                        account_number=account_number
                    )
                if bill_type == "PAYBILL":
                    resp, reference = pretium.pay_bill(
                        amount, short_code=short_code,
                        account_number=account_number
                    )
            except Exception as exception:
                raise ValueError(exception)
        else:
            url = "https://api.flutterwave.com/v3/billers/"\
                f"{biller_code}/items/{item_code}/payment"
            reference = secrets.token_hex(7)
            body = {
                "country": country,
                "customer_id": customer,
                "amount": int(amount),
                "reference": reference
            }

            try:
                req = requests.post(
                    url=url,
                    json=body,
                    headers=get_alt_flw_headers()
                )

                resp = req.json()
            except Exception as exception:
                resp = "unexpected error"
                print("unexpected exception: ", exception)

        return resp, reference

    def post(self, request, *args, **kwargs):
        serializer = serializers.CreateBillPaymentSerializerV2(
            data=request.data
        )

        if serializer.is_valid():
            country = serializer.validated_data['country']
            customer = serializer.validated_data['customer']
            bill_type = serializer.validated_data['bill_type']
            amount = serializer.validated_data['amount']
            crypto_amount = serializer.validated_data['crypto_amount']
            chain = serializer.validated_data['chain']
            email = serializer.validated_data.get('email')
            wallet_address = serializer.validated_data['wallet_address']
            transaction_hash = serializer.validated_data['transaction_hash']
            biller_code = serializer.validated_data.get('biller_code')
            item_code = serializer.validated_data.get('item_code')
            # timestamp = serializer.validated_data["timestamp"]
            _ = serializer.validated_data["offset"]
            data_package_id = serializer.validated_data.get("data_package_id")
            short_code = serializer.validated_data.get("short_code")
            account_number = serializer.validated_data.get("account_number")

            if data_package_id:
                data_package_id = int(data_package_id)

            if account_number is None:
                account_number = "any"

            try:
                client = Blockchain(key=os.getenv("TATUM_API_KEY"))
                chain_transaction = client.check_celo_transaction(
                    transaction_hash
                )
            except Exception as exception:
                raise exceptions.ValidationError(exception, code=400)

            sus = self.save_sus_transaction(
                amount=amount,
                chain=chain,
                crypto_amount=crypto_amount,
                bill_type=bill_type,
                email=email,
                wallet_address=wallet_address,
                transaction_hash=transaction_hash,
                biller_code=biller_code,
                item_code=item_code,
                short_code=short_code,
                customer=customer,
                country=country,
            )

            if client.is_supported_token(chain_transaction) is False:
                sus.error_message = "unsupported token"
                sus.save()
                raise exceptions.ValidationError(
                    "a Suspicious request", code=400)

            if not chain_transaction.get("status"):
                sus.save()
                raise exceptions.ValidationError(
                    "b Suspicious request", code=400)

            if chain_transaction.get("from").lower() != wallet_address.lower():
                sus.error_message = "doesn't come from the sender wallet"
                sus.save()
                raise exceptions.ValidationError(
                    "c Suspicious request", code=400)

            if client.is_cusd_destination(
                chain_transaction,
                os.getenv("CELO_MINI_MASTER_WALLET")
                    ) is False:
                sus.error_message = "doesn't go to master wallet"
                sus.save()
                raise exceptions.ValidationError(
                    "d Suspicious request",
                    code=400
                )

            if chain.lower() == "cusd":
                usd_amount = client.check_cusd_amount(
                    chain_transaction,
                    os.getenv("CELO_MINI_MASTER_WALLET")
                )
                usd_amount = round(usd_amount, 5)
                if float(crypto_amount) != usd_amount:
                    sus.error_message = f"{crypto_amount} != {usd_amount}"
                    sus.save()
                    raise exceptions.ValidationError(
                        "e Suspicious request", code=400)

            if chain.lower() == "usdt" or chain.lower() == "usdc":
                usd_amount = client.check_usdt_amount(
                    chain_transaction,
                    os.getenv("CELO_MINI_MASTER_WALLET")
                )
                usd_amount = round(usd_amount, 5)
                if float(crypto_amount) != usd_amount:
                    sus.error_message = f"{crypto_amount} != {usd_amount}"
                    sus.save()
                    raise exceptions.ValidationError(
                        "f Suspicious request", code=400)

            rate = get_naira_price(country)
            check_amount = rate * crypto_amount

            if float(amount) - check_amount > 0.5:
                sus.error_message = f"fiat {amount} - {check_amount} > 0.5"
                sus.save()
                raise exceptions.ValidationError(
                    "g Suspicious request", code=400)

            if Transaction.objects.filter(
                transaction_hash=transaction_hash
                    ).exists():
                sus.error_message = "transaction already exists"
                sus.save()
                raise exceptions.ValidationError("h Suspicious request")
            else:
                try:
                    payment, reference = self.initiate_payment(
                        biller_code=biller_code,
                        item_code=item_code,
                        country=country,
                        customer=customer,
                        amount=amount,
                        bill_type=bill_type,
                        data_package_id=data_package_id,
                        short_code=short_code,
                        account_number=account_number,
                    )
                except Exception as exception:
                    try:
                        transaction = models.Transaction(
                            amount=amount,
                            currency=chain,
                            currency_type="crypto",
                            crypto_amount=crypto_amount,
                            status="pending",
                            transaction_type=f"{bill_type} dapp",
                            email=email,
                            wallet_address=wallet_address,
                            transaction_hash=transaction_hash,
                            bill_type=bill_type,
                            biller_code=biller_code,
                            item_code=item_code,
                            short_code=short_code,
                            ref="invalid",
                            customer=customer,
                            country=country,
                            error_message=str(exception)
                        )
                        transaction.save()
                        raise exceptions.APIException(exception)
                    except Exception as exception:
                        raise exceptions.APIException(exception)

                try:
                    status = "pending"

                    transaction = models.Transaction(
                        amount=amount,
                        currency=chain,
                        currency_type="crypto",
                        crypto_amount=crypto_amount,
                        status=status,
                        transaction_type=f"{bill_type} dapp",
                        email=email,
                        wallet_address=wallet_address,
                        transaction_hash=transaction_hash,
                        bill_type=bill_type,
                        biller_code=biller_code,
                        item_code=item_code,
                        ref=reference,
                        short_code=short_code,
                        customer=customer,
                        country=country,
                    )
                    transaction.save()
                except Exception:
                    raise ValueError("Transaction failed to save")
                return response.Response(payment)
        else:
            raise exceptions.ValidationError(
                "You aren't passing in a value correctly"
            )


class CreateBillPaymentAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.CreateBillPaymentSerializer

    def initiate_payment(
            self, bill_type: str, amount: int,
            customer: str, country: str
            ):
        url = "https://api.flutterwave.com/v3/bills"

        reference = secrets.token_hex(7)

        body = {
            "country": country,
            "customer": customer,
            "amount": amount,
            "type": bill_type,
            "reference": reference
        }

        req = requests.post(
            url=url,
            json=body,
            headers=get_alt_flw_headers()
        )

        resp = req.json()
        if resp.get('status') == 'error':
            raise ValueError(resp.get('message'))

        return resp, reference

    def post(self, request, *args, **kwargs):
        serializer = serializers.CreateBillPaymentSerializer(
            data=self.request.data
        )

        if serializer.is_valid():
            country = serializer.validated_data['country']
            customer = serializer.validated_data['customer']
            bill_type = serializer.validated_data['bill_type']
            amount = serializer.validated_data['amount']
            crypto_amount = serializer.validated_data['crypto_amount']
            chain = serializer.validated_data['chain']
            email = serializer.validated_data.get('email')
            wallet_address = serializer.validated_data['wallet_address']
            transaction_hash = serializer.validated_data['transaction_hash']
            # timestamp = serializer.validated_data["timestamp"]
            # offset = serializer.validated_data["offset"]

            # client = Blockchain(key=os.getenv("TATUM_API_KEY"))
            # chain_transaction = client.check_celo_transaction(
            # transaction_hash)

            # if not chain_transaction.get("status"):
            #     raise exceptions.ValidationError(
            # "Shameless comrade", code=400)

            # if chain_transaction.get(
            # "from").lower() != wallet_address.lower():
            #     raise exceptions.ValidationError(
            # "Shameless comrade", code=400)

            # trans_timestamp = int(timestamp + (offset * 60))

            # celo_timestamp =  int(chain_transaction.get("timeStamp"))

            # if celo_timestamp - trans_timestamp > 120:
            #     print(celo_timestamp - trans_timestamp)
            #     print("omo")
            #     raise exceptions.ValidationError(
            # "Shameless comrade", code=400)

            try:
                payment, reference = self.initiate_payment(
                    bill_type=bill_type,
                    country=country,
                    customer=customer,
                    amount=amount,
                )
            except Exception as exception:
                raise ValueError(exception)

            try:
                status = "pending"

                if "airtime" in bill_type.lower():
                    status = "success"
                elif "data" in bill_type.lower():
                    status = "success"

                transaction = models.Transaction(
                    amount=amount,
                    currency=chain,
                    currency_type="crypto",
                    crypto_amount=crypto_amount,
                    status=status,
                    transaction_type=f"{bill_type} dapp",
                    email=email,
                    wallet_address=wallet_address,
                    transaction_hash=transaction_hash,
                    ref=reference,
                    customer=customer
                )
                transaction.save()
            except Exception:
                raise ValueError("Transaction failed to save")
            return response.Response(payment)
        else:
            raise exceptions.ValidationError(
                "You aren't passing in a value correctly"
            )


class GetDataPackages(views.APIView):
    permission_classes = [permissions.AllowAny,]

    def get(self, request, mobile_network_id: int):
        pretium_client = Pretium(api_key=os.getenv("PRETIUM_KEY"))

        packages = pretium_client.get_data_packages(mobile_network_id)
        return response.Response(packages)


class GetPretiumMobileNetworks(views.APIView):
    permission_classes = [permissions.AllowAny,]

    def get(self, request, country_name: str):
        pretium_client = Pretium(api_key=os.getenv("PRETIUM_KEY"))

        networks = pretium_client.get_mobile_networks(country_name)

        return response.Response(networks)


class GiftCardCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny,]
    queryset = models.GiftCard.objects.all()
    serializer_class = serializers.GiftCardSerializer
    filterset_fields = ["address",]


class RedeemCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny,]
    queryset = models.Redeem.objects.all()
    serializer_class = serializers.RedeemSerializer


class TransactionAPIView(generics.ListAPIView):
    filterset_fields = [
        'wallet_address', 'time', 'currency', 'status',
        'transaction_type', 'country', 'bill_type'
    ]
    search_fields = ['wallet_address', 'country']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend,]
    filterset_class = TransactionDateFilter
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.TransactionSerializer
    queryset = models.Transaction.objects.all().order_by("-id")


class TransactionOperaAPIView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    # authentication_classes = [OAuth2Authentication, ]
    permission_classes = [permissions.AllowAny,]
    filterset_fields = [
        'wallet_address', 'time', 'currency', 'status',
        'transaction_type', 'country', 'bill_type'
    ]
    search_fields = ['wallet_address', 'country']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend,]
    filterset_class = TransactionDateFilter
    serializer_class = serializers.TransactionSerializer
    queryset = models.Transaction.objects.all().order_by("-id")


class ValidateCustomerBet(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.ValidateCustomerBetSerializer

    def post(self, request, *args, **kwargs):
        serializer = serializers.ValidateCustomerBetSerializer(
            data=self.request.data
        )

        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            client_id = serializer.validated_data['client_id']

            if len(phone) != 13:
                raise ValueError("invalid phone number")

            bet9ja = Bet9ja(
                accountid=os.getenv("BET9JA_ACCOUNT_ID"),
                username=os.getenv("BET9JA_USERNAME"),
                password=os.getenv("BET9JA_PASSWORD"),
                secret_key=os.getenv("BET9JA_SECRET"),
            )

            try:
                resp = bet9ja.customer_validation(
                    phone=phone,
                    client_id=client_id,
                )
            except Exception as exception:
                raise ValueError(exception)

            return response.Response(resp)
        return response.Response(serializer.error_messages)


class CreateDepositNotificationAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.CreateDepositNotificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = serializers.CreateDepositNotificationSerializer(
            data=self.request.data
        )

        if serializer.is_valid():

            token = serializer.validated_data['token']
            amount = serializer.validated_data['amount']
            crypto_amount = serializer.validated_data['crypto_amount']
            chain = serializer.validated_data['chain']
            wallet_address = serializer.validated_data['wallet_address']
            transaction_hash = serializer.validated_data['transaction_hash']
            account_holder = serializer.validated_data['account_holder']
            client_id = serializer.validated_data['client_id']

            now = datetime.now()
            indt = now.strftime('%Y-%m-%d %H:%M:%S')
            reference = secrets.token_hex(7)

            # token = item_code
            # indt = short_code

            bet9ja = Bet9ja(
                accountid=os.getenv("BET9JA_ACCOUNT_ID"),
                username=os.getenv("BET9JA_USERNAME"),
                password=os.getenv("BET9JA_PASSWORD"),
                secret_key=os.getenv("BET9JA_SECRET"),
            )

            try:
                flw = FlutterWave(key=os.getenv("FLW_ALT_KEY"))
                flw.transfer_bet9ja(amount, reference)
            except Exception as exception:
                raise ValueError(exception)

            try:
                bet9ja.deposit_notification(
                    token=token,
                    amount=amount,
                    txid=reference,
                    indt=indt,
                    account_holder=account_holder,
                    client_id=client_id
                )
            except Exception as exception:
                raise ValueError(exception)

            transaction = models.Transaction(
                amount=amount,
                currency=chain,
                currency_type="crypto",
                crypto_amount=crypto_amount,
                status="pending",
                transaction_type="BET9JA_TOPUP",
                wallet_address=wallet_address,
                transaction_hash=transaction_hash,
                ref=reference,
                customer=client_id,
                account_name=account_holder,
                item_code=token,
                short_code=indt,
                bill_type="BET9JA_TOPUP",
            )
            transaction.save()

            return response.Response("topup processing..")


class CheckBetAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.CheckBetSerializer

    def post(self, request, *args, **kwargs):
        serializer = serializers.CheckBetSerializer(
            data=self.request.data
        )

        if serializer.is_valid():
            txid = serializer.validated_data['txid']

            bet9ja = Bet9ja(
                accountid=os.getenv("BET9JA_ACCOUNT_ID"),
                username=os.getenv("BET9JA_USERNAME"),
                password=os.getenv("BET9JA_PASSWORD"),
                secret_key=os.getenv("BET9JA_SECRET"),
            )

            try:
                resp = bet9ja.check_transaction(
                    txid=txid,
                )
            except Exception as exception:
                raise exceptions.APIException(exception)

            return response.Response(resp)
        return response.Response(serializer.error_messages)


class TransferAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.TransferSerializer

    def send_receipt(
            self, subject: str, message: str,
            from_email: str, recipient: str
            ):
        subject = subject
        message = message
        from_email = from_email
        recipient = recipient
        mail.send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[recipient],
        )
        return

    def save_sus_transaction(
            self, amount, chain, crypto_amount,
            bill_type, email="", wallet_address="",
            transaction_hash="", biller_code="",
            item_code="", short_code="",
            customer="", country="", reference=""
            ):
        transaction = models.Transaction(
            amount=amount,
            currency=chain,
            currency_type="crypto",
            crypto_amount=crypto_amount,
            status="failed",
            transaction_type=f"{bill_type} dapp",
            email=email,
            wallet_address=wallet_address,
            transaction_hash=transaction_hash,
            bill_type=bill_type,
            biller_code=biller_code,
            item_code=item_code,
            short_code=short_code,
            ref=f"sus-{reference}",
            customer=customer,
            country=country,
        )
        return transaction

    def get_currency(self, country: str):
        currency = {
            "GH": "GHS",
            "NG": "NGN"
        }
        return currency[country]

    def post(self, request, *args, **kwargs):
        serializer = serializers.TransferSerializer(
            data=self.request.data
        )

        if serializer.is_valid():
            transaction_hash = serializer.validated_data['transaction_hash']
            country = serializer.validated_data['country']
            customer = serializer.validated_data['customer']
            amount = serializer.validated_data['amount']
            crypto_amount = serializer.validated_data['crypto_amount']
            chain = serializer.validated_data['currency']
            wallet_address = serializer.validated_data['wallet_address']
            bank = serializer.validated_data['bank']
            narration = serializer.validated_data['narration']
            reference = secrets.token_hex(7)
            email = serializer.validated_data['email']
            fiat = serializer.validated_data['fiat_currency']
            beneficiary_name = serializer.validated_data['beneficiary_name']

            try:
                client = Blockchain(key=os.getenv("TATUM_API_KEY"))
                chain_transaction = client.check_celo_transaction(
                    transaction_hash
                )
            except Exception as exception:
                raise exceptions.ValidationError(exception, code=400)

            sus = self.save_sus_transaction(
                amount=amount,
                chain=chain,
                crypto_amount=crypto_amount,
                bill_type="FLW_TRANSFER",
                email=email,
                wallet_address=wallet_address,
                transaction_hash=transaction_hash,
                biller_code=bank,
                item_code=beneficiary_name,
                short_code="",
                customer=customer,
                country=country,
                reference=reference,
            )

            if client.is_supported_token(chain_transaction) is False:
                sus.error_message = "unsupported token"
                sus.ref = "sus_"+reference
                sus.save()
                raise exceptions.ValidationError(
                    "a Suspicious request", code=400)

            if not chain_transaction.get("status"):
                sus.ref = "sus_"+reference
                sus.save()
                raise exceptions.ValidationError(
                    "b Suspicious request", code=400)

            if chain_transaction.get("from").lower() != wallet_address.lower():
                sus.ref = "sus_"+reference
                sus.error_message = "doesn't come from the sender wallet"
                sus.save()
                raise exceptions.ValidationError(
                    "c Suspicious request", code=400)

            if client.is_cusd_destination(
                chain_transaction,
                os.getenv("CELO_MINI_MASTER_WALLET")
                    ) is False:
                sus.ref = "sus_"+reference
                sus.error_message = "doesn't go to master wallet"
                sus.save()
                raise exceptions.ValidationError(
                    "d Suspicious request",
                    code=400
                )

            if chain.lower() == "cusd":
                usd_amount = client.check_cusd_amount(
                    chain_transaction,
                    os.getenv("CELO_MINI_MASTER_WALLET")
                )
                usd_amount = round(usd_amount, 5)
                if float(crypto_amount) != usd_amount:
                    sus.ref = "sus_"+reference
                    sus.error_message = f"{crypto_amount} != {usd_amount}"
                    sus.save()
                    raise exceptions.ValidationError(
                        "e Suspicious request", code=400)

            if chain.lower() == "usdt" or chain.lower() == "usdc":
                usd_amount = client.check_usdt_amount(
                    chain_transaction,
                    os.getenv("CELO_MINI_MASTER_WALLET")
                )
                usd_amount = round(usd_amount, 5)
                if float(crypto_amount) != usd_amount:
                    sus.ref = "sus_"+reference
                    sus.error_message = f"{crypto_amount} != {usd_amount}"
                    sus.save()
                    raise exceptions.ValidationError(
                        "f Suspicious request", code=400)

            rate = get_naira_price(country)
            check_amount = rate * float(crypto_amount)

            if float(amount) - check_amount > 0.5:
                sus.ref = "sus_"+reference
                sus.error_message = f"fiat {amount} - {check_amount} > 0.5"
                sus.save()
                raise exceptions.ValidationError(
                    "g Suspicious request", code=400)

            if Transaction.objects.filter(
                transaction_hash=transaction_hash
                    ).exists():
                sus.ref = "sus_"+reference
                sus.error_message = "transaction already exists"
                sus.save()
                raise exceptions.ValidationError("h Suspicious request")

            flw = FlutterWave(key=os.getenv("FLW_ALT_KEY"))

            sus.ref = reference
            sus.status = "pending"
            sus.save()
            # currency = self.get_currency(country)

            txn = flw.transfer(
                bank, customer,
                amount, narration,
                fiat, reference,
                fiat, beneficiary_name
            )

            sus.transfer_id = txn.get("data").get("id")
            return response.Response("success")
        else:
            raise exceptions.ValidationError(serializer.error_messages)


class GetBankList(views.APIView):
    permission_classes = [permissions.AllowAny,]

    def get(self, request, country: str):
        flw_client = FlutterWave(key=os.getenv("FLW_ALT_KEY"))

        banks = flw_client.get_banks(country)

        return response.Response(banks)


class CreateStellarBillPaymentAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.CreateStellarBillPaymentSerializer

    def save_sus_transaction(
            self, amount, chain, crypto_amount,
            bill_type, email="", wallet_address="",
            transaction_hash="", biller_code="",
            item_code="", short_code="",
            customer="", country=""
            ):
        reference = secrets.token_hex(7)
        transaction = models.StellarTransaction(
            amount=amount,
            currency=chain,
            currency_type="crypto",
            crypto_amount=crypto_amount,
            status="failed",
            transaction_type=f"{bill_type} dapp",
            email=email,
            wallet_address=wallet_address,
            transaction_hash=transaction_hash,
            bill_type=bill_type,
            biller_code=biller_code,
            item_code=item_code,
            short_code=short_code,
            ref=f"sus-{reference}",
            customer=customer,
            country=country,
        )
        return transaction

    def initiate_payment(
            self, biller_code, item_code, country,
            customer, amount, bill_type="", data_package_id=0, short_code="",
            account_number=""
            ):

        if country == "KE" or country == "ZA" or country == "UG":
            pretium = Pretium(api_key=os.getenv("PRETIUM_KEY"))

            try:

                if bill_type == "AIRTIME":
                    resp, reference = pretium.buy_airtime(
                        amount, customer, country
                    )
                if bill_type == "MOBILEDATA":
                    resp, reference = pretium.buy_data(
                        amount, customer,
                        data_package_id
                    )
                if bill_type == "BUY_GOODS":
                    resp, reference = pretium.buy_goods(
                        amount, short_code=short_code,
                        account_number=account_number
                    )
                if bill_type == "PAYBILL":
                    resp, reference = pretium.pay_bill(
                        amount, short_code=short_code,
                        account_number=account_number
                    )
            except Exception as exception:
                raise ValueError(exception)
        else:
            url = "https://api.flutterwave.com/v3/billers/"\
                f"{biller_code}/items/{item_code}/payment"
            reference = secrets.token_hex(7)
            body = {
                "country": country,
                "customer_id": customer,
                "amount": int(amount),
                "reference": reference
            }

            try:
                req = requests.post(
                    url=url,
                    json=body,
                    headers=get_alt_flw_headers()
                )

                resp = req.json()
            except Exception as exception:
                resp = "unexpected error"
                print("unexpected exception: ", exception)

        return resp, reference

    def post(self, request, *args, **kwargs):
        serializer = serializers.CreateStellarBillPaymentSerializer(
            data=request.data
        )

        if serializer.is_valid():
            country = serializer.validated_data['country']
            customer = serializer.validated_data['customer']
            bill_type = serializer.validated_data['bill_type']
            amount = serializer.validated_data['amount']
            crypto_amount = serializer.validated_data['crypto_amount']
            chain = serializer.validated_data['chain']
            email = serializer.validated_data.get('email')
            wallet_address = serializer.validated_data['wallet_address']
            transaction_hash = serializer.validated_data['transaction_hash']
            biller_code = serializer.validated_data.get('biller_code')
            item_code = serializer.validated_data.get('item_code')
            # timestamp = serializer.validated_data["timestamp"]
            # _ = serializer.validated_data["offset"]
            # data_package_id = serializer.validated_data.get("data_package_id")
            short_code = serializer.validated_data.get("short_code")
            account_number = serializer.validated_data.get("account_number")

            # if data_package_id:
            #     data_package_id = int(data_package_id)

            if account_number is None:
                account_number = "any"

            try:
                client = Stellar(net="test")
                chain_transaction = client.get_contract_payment_details(
                    transaction_hash
                )
                print("chain transaction: ", chain_transaction)
            except Exception as exception:
                raise exceptions.ValidationError(exception, code=400)

            sus = self.save_sus_transaction(
                amount=amount,
                chain=chain,
                crypto_amount=crypto_amount,
                bill_type=bill_type,
                email=email,
                wallet_address=wallet_address,
                transaction_hash=transaction_hash,
                biller_code=biller_code,
                item_code=item_code,
                short_code=short_code,
                customer=customer,
                country=country,
            )

            rate = get_naira_price(country)
            check_amount = rate * crypto_amount

            if models.StellarTransaction.objects.filter(
                transaction_hash=transaction_hash
                    ).exists():
                sus.error_message = "transaction already exists"
                sus.save()
                raise exceptions.ValidationError("h Suspicious request")
            else:
                try:
                    payment, reference = self.initiate_payment(
                        biller_code=biller_code,
                        item_code=item_code,
                        country=country,
                        customer=customer,
                        amount=amount,
                        bill_type=bill_type,
                        data_package_id=0,
                        short_code="",
                        account_number=account_number,
                    )
                except Exception as exception:
                    try:
                        transaction = models.StellarTransaction(
                            amount=amount,
                            currency=chain,
                            currency_type="crypto",
                            crypto_amount=crypto_amount,
                            status="pending",
                            transaction_type=f"{bill_type} dapp",
                            email=email,
                            wallet_address=wallet_address,
                            transaction_hash=transaction_hash,
                            bill_type=bill_type,
                            biller_code=biller_code,
                            item_code=item_code,
                            short_code=short_code,
                            ref="invalid",
                            customer=customer,
                            country=country,
                            error_message=str(exception)
                        )
                        transaction.save()
                        raise exceptions.APIException(exception)
                    except Exception as exception:
                        raise exceptions.APIException(exception)

                try:
                    status = "pending"

                    transaction = models.StellarTransaction(
                        amount=amount,
                        currency=chain,
                        currency_type="crypto",
                        crypto_amount=crypto_amount,
                        status=status,
                        transaction_type=f"{bill_type} dapp",
                        email=email,
                        wallet_address=wallet_address,
                        transaction_hash=transaction_hash,
                        bill_type=bill_type,
                        biller_code=biller_code,
                        item_code=item_code,
                        ref=reference,
                        short_code=short_code,
                        customer=customer,
                        country=country,
                    )
                    transaction.save()
                except Exception:
                    raise ValueError("Transaction failed to save")
                return response.Response(payment)
        else:
            print(serializer.errors)
            raise exceptions.ValidationError(
                "You aren't passing in a value correctly"
            )


class StellarTransactionAPIView(generics.ListAPIView):
    filterset_fields = [
        'wallet_address', 'time', 'currency', 'status',
        'transaction_type', 'country', 'bill_type'
    ]
    search_fields = ['wallet_address', 'country']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend,]
    filterset_class = StellarTransactionDateFilter
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.StellarTransactionSerializer
    queryset = models.StellarTransaction.objects.all().order_by("-id")


class StellarGiftCardAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.StellarGiftCardSerializer
    queryset = models.StellarGiftCard.objects.all()
    permission_classes = [permissions.AllowAny,]

    def perform_create(self, serializer, **kwargs):
        try:
            code = secrets.token_hex(16)
            kwargs['code'] = code
        except Exception as exception:
            raise ValueError(exception)
        serializer.save(**kwargs)

        return response.Response(code)


class RedeemStellarAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.StellarRedeemSerializer
    queryset = models.RedeemStellar.objects.all()
    permission_classes = [permissions.AllowAny,]

    def perform_create(self, serializer, **kwargs):
        code = serializer.validated_data.get("code")
        giftcard = models.StellarGiftCard.objects.get(code=code)

        try:
            admin_wallet = AdminWallet.objects.get(
                network__iexact="stellar_usdc")
        except AdminWallet.DoesNotExist:
            raise ValueError("admin wallet not found")

        client = Blockchain(
            key=str(os.getenv("TATUM_API_KEY"))
        )
        secret_key = client.decrypt_crendentails(
            str(admin_wallet.private_key)
        )

        stellar = Stellar("test")
        txn = stellar.build_usdc_transaction(
            secret_key=secret_key,
            destination=giftcard.wallet,
            amount=Decimal(giftcard.amount),
        )

        stellar.sign_and_submit_transaction(
            txn,
            secret_key=secret_key
        )

        serializer.save(**kwargs)

        response.Response("redeemed")


class TransactionOperaDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.TransactionSerializer
    queryset = models.Transaction.objects.all()
    lookup_field = "transaction_hash"


class UniqueWalletAddressesView(views.APIView):
    """
    API endpoint that returns a list of unique wallet addresses from transactions.
    Excludes null values and empty strings.
    """
    permission_classes = [permissions.AllowAny,]

    def get(self, request):
        try:
            # Get unique wallet addresses, excluding null and empty strings
            wallet_addresses = models.Transaction.objects.exclude(
                Q(wallet_address__isnull=True) | 
                Q(wallet_address='')
            ).values_list('wallet_address', flat=True).distinct()

            # Convert QuerySet to list
            wallet_addresses_list = list(wallet_addresses)

            return response.Response({
                'status': 'success',
                'count': len(wallet_addresses_list),
                'wallet_addresses': wallet_addresses_list
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return response.Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetSochitelOperators(views.APIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.SochitelOperatorSerializer
    country = openapi.Parameter(
        'bill-type', openapi.IN_QUERY,
        description="example: NG, GH", type=openapi.TYPE_STRING
    )
    product_type = openapi.Parameter(
        'product_type', openapi.IN_QUERY,
        description="""
        example:
        1 (MOBILE_TOP_UP),
        2 (MOBILE_PIN),
        3 (BILL_PAYMENT),
        4 (MOBILE_DATA)
        """,
        type=openapi.TYPE_NUMBER
    )

    def get_operators(
            self, country: str,
            product_type: sochitel.ProductTypeEnum | None = None
            ) -> List[Dict[str, Any]]:
        testuser = sochitel.TestUsers.USER1
        client = sochitel.Client.create_staging_client(
            testuser
        )

        return client.get_operators(
            country=country,
            product_type=product_type
            ).to_array()

    def get(self, request, *args, **kwargs):
        country = request.query_params.get('country')
        product_type = request.query_params.get('product_type')

        operators = self.get_operators(
            country=country, product_type=product_type
            )

        return response.Response(operators)


class SochitelTransactionExecuteView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.SochitelTransactionRequestSerializer

    def __init__(self, **kwargs):
        testuser = sochitel.TestUsers.USER1
        super().__init__(**kwargs)
        # Initialize Sochitel client
        self.client = sochitel.Client.create_staging_client(
            testuser
        )

    def post(self, request):
        """
        Execute a Sochitel transaction.
        """
        serializer = serializers.SochitelTransactionRequestSerializer(
            data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            # Create transaction request
            transaction_request = ExecTransactionRequest(
                operator=serializer.validated_data['operator'],
                msisdn=serializer.validated_data.get('msisdn'),
                account_id=serializer.validated_data.get('account_id'),
                amount=serializer.validated_data.get('amount'),
                amount_operator=serializer.validated_data.get(
                    'amount_operator'
                ),
                product_id=serializer.validated_data.get('product_id'),
                user_reference=serializer.validated_data.get('user_reference'),
                extra_parameters=serializer.validated_data.get('extra_parameters')
            )

            # Execute transaction
            result = self.client.exec_transaction(transaction_request)

            return response.Response(result, status=status.HTTP_200_OK)

        except rest_serializers.ValidationError as e:
            return response.Response(
                {'error': 'Validation error', 'details': e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except APIError as e:
            return response.Response(
                {
                    'error': 'Sochitel API error',
                    'code': e.status_id,
                    'message': e.status_name
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except InvalidOperation:
            return response.Response(
                {'error': 'Invalid amount format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return response.Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
