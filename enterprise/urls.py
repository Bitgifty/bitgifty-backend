from django.urls import path

from . import views


urlpatterns = [
    path(
        'giftcard/list-giftcard-images/',
        views.ListGiftCardImageAPIView.as_view()
    ),
    path('giftcard/list-giftcards/', views.ListGiftCard.as_view()),
    path('giftcard/create-giftcard/', views.CreateGiftCardAPIView.as_view()),
    path(
        'utilities/list-bill-categories/',
        views.GetBillCategoriesAPIView.as_view()),
    path(
        'utilities/list-bill-info/',
        views.GetBillInfo.as_view()),
    path(
        'utilities/validate-customer/',
        views.ValidateCustomerDetails.as_view()),
    path(
        'utilities/create-bill-transaction/',
        views.CreateBillTransaction.as_view()),
    path(
        'utilities/payment-status/',
        views.GetPaymentStatus.as_view()),
    path(
        'utilities/transactions/',
        views.GetTransactionAPIView.as_view()
    ),
    path(
        'user/',
        views.GetUser.as_view()
    ),
]
