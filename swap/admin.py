from django.contrib import admin
from .models import SwapTable, USDTNaira, USDTPrice
# Register your models here.
admin.site.register([SwapTable, USDTNaira, USDTPrice])
