from django_filters import FilterSet, NumberFilter, CharFilter
from .models import Product


class ProductFilter(FilterSet):
    price_min = NumberFilter(field_name='price', lookup_expr='gte')
    price_max = NumberFilter(field_name='price', lookup_expr='lte')
    ram_min = NumberFilter(field_name='smartphone__ram_gb', lookup_expr='gte')

    class Meta:
        model = Product
        fields = ['brand', 'category', 'price_min', 'price_max', 'ram_min']
