from django.contrib import admin
from . import models

# Register your models here.

admin.site.register([models.GiftCard, models.AdminWallet, models.Reward])


@admin.register(models.Redeem)
class RedeemAdmin(admin.ModelAdmin):
    list_display = ('address', 'code', 'redemption_date')
    list_filter = ('address', 'code', 'redemption_date')
    search_fields = ('address', 'code', 'redemption_date')


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('status', 'wallet_address', 'country', 'time')
    list_filter = ('status', 'country')
    search_fields = ('status', 'wallet_address', 'country', 'time')


@admin.register(models.CashBack)
class CashbackAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount')
    list_filter = ('wallet', 'amount')
    search_fields = ('wallet', 'amount')
