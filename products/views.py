from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Product, Smartphone, Laptop
from .serializers import ProductSerializer, SmartphoneSerializer, LaptopSerializer
from .filters import ProductFilter
from .pagination import StandardPagination


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'brand']
    ordering_fields = ['price', 'updated_at']
    pagination_class = StandardPagination


class SmartphoneViewSet(viewsets.ModelViewSet):
    queryset = Smartphone.objects.all()
    serializer_class = SmartphoneSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['brand', 'os', 'ram_gb']
    search_fields = ['name', 'brand']
    ordering_fields = ['price', 'updated_at']
    pagination_class = StandardPagination


class LaptopViewSet(viewsets.ModelViewSet):
    queryset = Laptop.objects.all()
    serializer_class = LaptopSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['brand', 'cpu']
    search_fields = ['name', 'brand']
    ordering_fields = ['price', 'updated_at']
    pagination_class = StandardPagination
