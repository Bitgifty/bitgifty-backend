from django.contrib import admin
from .models import SwapTable, USDTNaira, USDTPrice, Swap
# Register your models here.
admin.site.register([SwapTable, USDTNaira, USDTPrice])

@admin.register(Swap)
class SwapAdmin(admin.ModelAdmin):
    list_display = ('swap_amount', 'swap_from_wallet', 'swap_to_wallet', 'released_naira')

    def swap_from_wallet(self, obj):
        if obj.swap_from:
            email = obj.swap_from.owner.email
        else:
            email = ""
        return email
    
    def swap_to_wallet(self, obj):
        if obj.swap_to:
            email = obj.swap_to.owner.email
        else:
            email = ""
        return email
    
    def released_naira(self, obj):
       swap_amount=float(obj.swap_amount)
       factor=float(obj.swap_table.naira_factor.price)
       usdt_price=obj.swap_table.usd_price.price

       amount = factor * usdt_price * swap_amount
       return amount