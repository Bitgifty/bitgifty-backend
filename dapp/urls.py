from django.urls import path, include

from . import views

urlpatterns = [
    path('get-fee/', views.GetFeesAPIView.as_view()),
    path('create-bill-transaction/', views.CreateBillPaymentAPIView.as_view()),
    path('get-bill-categories/', views.GetBillCategoriesAPIView.as_view()),
    path(
        'v2/get-bill-categories/',
        views.GetBillCategoriesV2APIView.as_view()),
    path('v2/get-biller-info/', views.GetBillerInfoAPIView.as_view()),
    path('v2/get-bill-info/', views.GetBillInfoAPIView.as_view()),
    path(
        'v2/create-bill-transaction/',
        views.CreateBillPaymentV2APIView.as_view()),
    path(
        'v2/get-mobile-networks/<str:country_name>/',
        views.GetPretiumMobileNetworks.as_view()),
    path(
        'v2/get-data-packages/<int:mobile_network_id>/',
        views.GetDataPackages.as_view()),
    path('validate-bill-service/', views.ValidateBillServiceAPIView.as_view()),
    path('create-giftcard/', views.GiftCardCreateAPIView.as_view()),
    path('redeem-giftcard/', views.RedeemCreateAPIView.as_view()),
    path('transactions/', views.TransactionAPIView.as_view()),

    path('client/transactions/', views.TransactionOperaAPIView.as_view()),
    path(
        'client/unique-addresses/',
        views.UniqueWalletAddressesView.as_view()
    ),
    path(
        'client/transactions/<str:transaction_hash>/',
        views.TransactionOperaDetailAPIView.as_view()
    ),
    path("o/", include('oauth2_provider.urls', namespace='oauth2_provider')),
    path(
        'bet/validate-customer/',
        views.ValidateCustomerBet.as_view(),
    ),
    path(
        'bet/create-deposit-notification/',
        views.CreateDepositNotificationAPIView.as_view(),
    ),
    path(
        'bet/check-bet/',
        views.CheckBetAPIView.as_view(),
    ),
    path(
        'flw/transfer/',
        views.TransferAPIView.as_view(),
    ),
    path(
        'flw/get-banks/<str:country>/',
        views.GetBankList.as_view()),
    path(
        'stellar/create-bill-transaction/',
        views.CreateStellarBillPaymentAPIView.as_view()),
    path('stellar/transactions/', views.StellarTransactionAPIView.as_view()),
    path('stellar/giftcard/create/', views.StellarGiftCardAPIView.as_view()),
    path('stellar/giftcard/redeem/', views.RedeemStellarAPIView.as_view()),

    path('sochitel/get-operators/', views.GetSochitelOperators.as_view()),
    path(
        'sochitel/exec-transaction/',
        views.SochitelTransactionExecuteView.as_view()
    ),
]
