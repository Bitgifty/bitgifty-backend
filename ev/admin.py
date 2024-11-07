from django.contrib import admin
from .models import EVItem, EVCategory, EVStore, EVSuperCategory, EVOrder, EVOrderItem, EVShippingAddress

admin.site.register([EVItem, EVCategory, EVStore, EVSuperCategory, EVShippingAddress, EVOrderItem, EVOrder])
