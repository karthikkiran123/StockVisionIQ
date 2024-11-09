from django.contrib import admin
from . models.vendor import Vendor
from .models.product import Product

# Register your models here.
admin.site.register(Vendor)
admin.site.register(Product)