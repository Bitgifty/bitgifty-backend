from django.contrib import admin
from . import models
# Register your models here.

admin.site.register([
    models.AirtimePurchase,
    models.Cable,
    models.CablePlan,
    models.CablePurchase,
    models.DataPlan,
    models.DataPurchase,
    models.Disco,
    models.ElectricityPurchase,
    models.Network
])