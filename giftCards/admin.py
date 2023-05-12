from django.contrib import admin
from .models import GiftCard, Redeem, GiftCardImage,GiftCardFee
# Register your models here.

admin.site.register([GiftCard, Redeem, GiftCardImage, GiftCardFee])
