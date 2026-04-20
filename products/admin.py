from django.contrib import admin
from .models import Product, Smartphone, Laptop


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'price', 'updated_at']
    list_filter = ['category', 'brand', 'updated_at']
    search_fields = ['name', 'brand']


@admin.register(Smartphone)
class SmartphoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'price', 'os', 'ram_gb', 'storage_gb']
    list_filter = ['os', 'brand', 'ram_gb']
    search_fields = ['name', 'brand']


@admin.register(Laptop)
class LaptopAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'price', 'cpu', 'ram_gb', 'storage_gb']
    list_filter = ['cpu', 'brand', 'ram_gb']
    search_fields = ['name', 'brand']
