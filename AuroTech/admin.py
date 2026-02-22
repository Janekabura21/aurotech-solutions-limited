from django.contrib import admin

# Register your models here.
from .models import CoreProduct, Product


admin.site.register(CoreProduct)
admin.site.register(Product)


