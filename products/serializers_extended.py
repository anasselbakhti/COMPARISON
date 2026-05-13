# ============================================================
#  products/serializers_extended.py  —  Pour Compare & Notifications
#  À AJOUTER aux serializers existants
# ============================================================
from rest_framework import serializers
from .models import Product, Smartphone, Laptop
from .notifications import NotificationModel, NotificationService
from .compare import ProductComparer


# ============================================================
# SERIALIZERS - NOTIFICATIONS
# ============================================================
class NotificationSerializer(serializers.ModelSerializer):
    """Serializer pour les notifications."""
    
    class Meta:
        model = NotificationModel
        fields = ['id', 'user', 'notification_type', 'title', 'message', 'is_read', 'created_at', 'read_at']
        read_only_fields = ['id', 'created_at', 'read_at', 'user']


class NotificationCreateSerializer(serializers.Serializer):
    """Serializer pour créer une notification."""
    notification_type = serializers.ChoiceField(choices=['price_drop', 'new_product', 'comparison', 'restock', 'system'])
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    
    def create(self, validated_data):
        user = self.context['request'].user
        return NotificationService.create_notification(
            user=user,
            **validated_data
        )


# ============================================================
# SERIALIZERS - COMPARE
# ============================================================
class ComparisonRequestSerializer(serializers.Serializer):
    """Serializer pour demander une comparaison."""
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Liste des IDs de produits à comparer"
    )
    
    def validate_product_ids(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Au moins 2 produits requis pour comparer.")
        if len(value) > 5:
            raise serializers.ValidationError("Maximum 5 produits par comparaison.")
        return value


class ComparisonResultSerializer(serializers.Serializer):
    """Serializer pour le résultat d'une comparaison."""
    products = serializers.ListField()
    cheapest = serializers.DictField()
    best_rated = serializers.DictField()


class FilterCriteriaSerializer(serializers.Serializer):
    """Serializer pour filtrer les produits."""
    category = serializers.ChoiceField(choices=['smartphone', 'laptop'])
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    min_rating = serializers.IntegerField(required=False, default=0)
