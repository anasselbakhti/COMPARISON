# ============================================================
#  products/compare.py  —  Personne 1 (Ami)
#  Service de comparaison de produits
# ============================================================
from django.db.models import Q
from decimal import Decimal
from .models import Product, Smartphone, Laptop


class ProductComparer:
    """
    Service pour comparer deux ou plusieurs produits.
    Retourne les différences clés et les points forts/faibles.
    """
    
    @staticmethod
    def compare_two_products(product_id_1, product_id_2):
        """
        Compare deux produits détaillés.
        """
        try:
            product1 = Product.objects.get(id=product_id_1)
            product2 = Product.objects.get(id=product_id_2)
        except Product.DoesNotExist:
            return {'error': 'Produit non trouvé'}
        
        # Récupérer les specs
        specs1 = product1.get_specs()
        specs2 = product2.get_specs()
        
        # Créer la comparaison
        comparison = {
            'product1': {
                'id': product1.id,
                'name': product1.name,
                'brand': product1.brand,
                'price': float(product1.price),
                'specs': specs1,
                'rating': product1.get_avg_rating(),
            },
            'product2': {
                'id': product2.id,
                'name': product2.name,
                'brand': product2.brand,
                'price': float(product2.price),
                'specs': specs2,
                'rating': product2.get_avg_rating(),
            },
            'price_difference': float(abs(product1.price - product2.price)),
            'price_winner': 'product1' if product1.price < product2.price else 'product2',
            'rating_winner': 'product1' if product1.get_avg_rating() > product2.get_avg_rating() else 'product2',
        }
        
        return comparison
    
    @staticmethod
    def compare_multiple_products(product_ids):
        """
        Compare plusieurs produits à la fois.
        """
        products = Product.objects.filter(id__in=product_ids)
        
        if not products.exists():
            return {'error': 'Aucun produit trouvé'}
        
        comparison_data = []
        for product in products:
            comparison_data.append({
                'id': product.id,
                'name': product.name,
                'brand': product.brand,
                'price': float(product.price),
                'category': product.category,
                'specs': product.get_specs(),
                'rating': product.get_avg_rating(),
            })
        
        return {
            'products': comparison_data,
            'cheapest': min(comparison_data, key=lambda x: x['price']),
            'best_rated': max(comparison_data, key=lambda x: x['rating']),
        }
    
    @staticmethod
    def filter_by_criteria(category, min_price=0, max_price=None, min_rating=0):
        """
        Filtre les produits selon les critères et retourne les meilleurs.
        """
        queryset = Product.objects.filter(
            category=category,
            price__gte=min_price
        )
        
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Ajouter la note moyenne
        products = []
        for product in queryset:
            avg_rating = product.get_avg_rating()
            if avg_rating >= min_rating:
                products.append({
                    'id': product.id,
                    'name': product.name,
                    'brand': product.brand,
                    'price': float(product.price),
                    'specs': product.get_specs(),
                    'rating': avg_rating,
                })
        
        return sorted(products, key=lambda x: x['rating'], reverse=True)
