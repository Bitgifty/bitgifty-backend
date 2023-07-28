from django.contrib import admin
from .models import GiftCard, Redeem, GiftCardImage,GiftCardFee
# Register your models here.

admin.site.register([Redeem, GiftCardImage, GiftCardFee])




@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = ('email', 'currency', 'amount', 'receipent_email', 'note', 'code', 'status', 'creation_date')
    list_filter = ('currency', 'amount', 'receipent_email', 'note', 'code', 'status', 'creation_date')
    search_fields = ('currency', 'amount', 'receipent_email', 'note', 'code', 'status', 'creation_date')

    def email(self, obj):
        if obj.wallet:
            email = obj.wallet.owner.email
        else:
            email = ""
        return email
