from django.contrib import admin
from .models import GiftCard, Redeem, GiftCardImage
# Register your models here.

admin.site.register([GiftCard, Redeem, GiftCardImage])
