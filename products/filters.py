# ============================================================
#  products/filters.py  —  Personne 1
# ============================================================
from django_filters import rest_framework as filters
from .models import Product, Smartphone, Laptop


class ProductFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model  = Product
        fields = ['brand', 'category', 'price_min', 'price_max']


class SmartphoneFilter(filters.FilterSet):
    price_min    = filters.NumberFilter(field_name='price',        lookup_expr='gte')
    price_max    = filters.NumberFilter(field_name='price',        lookup_expr='lte')
    ram_min      = filters.NumberFilter(field_name='ram_gb',       lookup_expr='gte')
    battery_min  = filters.NumberFilter(field_name='battery_mah',  lookup_expr='gte')
    year_min     = filters.NumberFilter(field_name='release_year', lookup_expr='gte')
    year_max     = filters.NumberFilter(field_name='release_year', lookup_expr='lte')
    release_year = filters.NumberFilter(field_name='release_year', lookup_expr='exact')

    class Meta:
        model  = Smartphone
        fields = ['brand', 'os', 'network', 'price_min', 'price_max',
                  'ram_min', 'battery_min', 'release_year', 'year_min', 'year_max']


class LaptopFilter(filters.FilterSet):
    price_min    = filters.NumberFilter(field_name='price',        lookup_expr='gte')
    price_max    = filters.NumberFilter(field_name='price',        lookup_expr='lte')
    ram_min      = filters.NumberFilter(field_name='ram_gb',       lookup_expr='gte')
    year_min     = filters.NumberFilter(field_name='release_year', lookup_expr='gte')
    year_max     = filters.NumberFilter(field_name='release_year', lookup_expr='lte')
    release_year = filters.NumberFilter(field_name='release_year', lookup_expr='exact')

    class Meta:
        model  = Laptop
        fields = ['brand', 'os', 'price_min', 'price_max', 'ram_min',
                  'release_year', 'year_min', 'year_max']