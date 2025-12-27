from django.contrib import admin

from apps.products.models import ProductCategory, Product

admin.site.register(ProductCategory)
admin.site.register(Product)
