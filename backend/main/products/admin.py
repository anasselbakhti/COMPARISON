# ============================================================
#  products/admin.py  —  Personne 1
# ============================================================
from django.contrib import admin
from .models import Product, Smartphone, Laptop, UserProfile, Favorite, Review, SavedComparison, PriceAlert, Notification


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['id', 'name', 'brand', 'category', 'price', 'updated_at']
    list_filter   = ['brand', 'category']
    search_fields = ['name', 'brand']


@admin.register(Smartphone)
class SmartphoneAdmin(admin.ModelAdmin):
    list_display  = ['id', 'name', 'brand', 'price', 'os', 'ram_gb', 'camera_mp', 'battery_mah']
    list_filter   = ['brand', 'os', 'network', 'ram_gb']
    search_fields = ['name', 'brand']


@admin.register(Laptop)
class LaptopAdmin(admin.ModelAdmin):
    list_display  = ['id', 'name', 'brand', 'price', 'cpu', 'ram_gb', 'storage_gb']
    list_filter   = ['brand', 'os', 'ram_gb']
    search_fields = ['name', 'brand', 'cpu']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'phone', 'city', 'created_at']
    search_fields = ['user__username', 'city']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'product', 'added_at']
    list_filter   = ['user']
    search_fields = ['user__username', 'product__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'product__name', 'comment']


@admin.register(SavedComparison)
class SavedComparisonAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'created_at']
    filter_horizontal = ['products']
    search_fields = ['user__username', 'name']


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'target_price', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'product__name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'message']