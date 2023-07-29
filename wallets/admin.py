from django.contrib import admin
from .models import Wallet
# Register your models here.

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('email', 'network', 'balance')
    list_filter = ('network', 'balance')
    search_fields = ('network', 'balance')

    def email(self, obj):
        return obj.owner.email
