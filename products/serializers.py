# ============================================================
#  products/serializers.py  —  Personne 1
#  Sérialisation : Auth (Register/Login) + Profil + Favoris
# ============================================================
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product, Smartphone, Laptop, UserProfile, Favorite, Review, SavedComparison, PriceAlert
from .notifications import NotificationModel


# ============================================================
# AUTH — Inscription
# ============================================================
class RegisterSerializer(serializers.ModelSerializer):
    # Le mot de passe ne doit jamais être renvoyé dans la réponse
    password  = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, label="Confirmer le mot de passe")

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'password', 'password2']

    def validate(self, data):
        """Vérifie que les 2 mots de passe correspondent."""
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def create(self, validated_data):
        """Crée l'utilisateur + son profil automatiquement."""
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        # Crée le profil lié automatiquement
        UserProfile.objects.create(user=user)
        return user


# ============================================================
# AUTH — Affichage utilisateur connecté
# ============================================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'date_joined']


# ============================================================
# PROFIL UTILISATEUR
# ============================================================
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email    = serializers.CharField(source='user.email',    read_only=True)

    class Meta:
        model  = UserProfile
        fields = ['id', 'username', 'email', 'phone', 'city', 'avatar', 'created_at']


# ============================================================
# PRODUIT — version légère pour les favoris
# ============================================================
class ProductMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Product
        fields = ['id', 'name', 'brand', 'category', 'price']


# ============================================================
# FAVORIS
# ============================================================
class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductMiniSerializer(read_only=True)           # affichage
    product_id = serializers.PrimaryKeyRelatedField(          # écriture
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model  = Favorite
        fields = ['id', 'product', 'product_id', 'added_at']

    def create(self, validated_data):
        """Associe automatiquement le user connecté au favori."""
        user = self.context['request'].user
        product = validated_data['product']

        # Vérifie si le favori existe déjà
        if Favorite.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("Ce produit est déjà dans vos favoris.")

        return Favorite.objects.create(user=user, product=product)


# ============================================================
# SERIALIZERS PRODUITS (utilisés aussi par Personne 2)
# ============================================================
class SmartphoneSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model  = Smartphone
        fields = [
            'id', 'name', 'brand', 'price', 'source_url',
            'os', 'ram_gb', 'storage_gb', 'camera_mp',
            'battery_mah', 'screen_in', 'network',
            'avg_rating', 'updated_at',
        ]

    def get_avg_rating(self, obj):
        return obj.get_avg_rating()


class LaptopSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model  = Laptop
        fields = [
            'id', 'name', 'brand', 'price', 'source_url',
            'cpu', 'ram_gb', 'storage_gb', 'screen_in',
            'gpu', 'battery_wh', 'weight_kg', 'os',
            'avg_rating', 'updated_at',
        ]

    def get_avg_rating(self, obj):
        return obj.get_avg_rating()


class ProductSerializer(serializers.ModelSerializer):
    specs      = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = ['id', 'name', 'brand', 'category', 'price',
                  'source_url', 'specs', 'avg_rating', 'updated_at']

    def get_specs(self, obj):
        return obj.get_specs()

    def get_avg_rating(self, obj):
        return obj.get_avg_rating()


# ============================================================
# AVIS (Review)
# ============================================================
class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model  = Review
        fields = ['id', 'username', 'product', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'username', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data['product']
        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("Vous avez déjà soumis un avis pour ce produit.")
        return Review.objects.create(user=user, **validated_data)


# ============================================================
# COMPARAISONS SAUVEGARDÉES
# ============================================================
class SavedComparisonSerializer(serializers.ModelSerializer):
    products = ProductMiniSerializer(many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='products',
        many=True,
        write_only=True
    )

    class Meta:
        model  = SavedComparison
        fields = ['id', 'title', 'products', 'product_ids', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_product_ids(self, value):
        if not (2 <= len(value) <= 4):
            raise serializers.ValidationError("Vous devez sélectionner entre 2 et 4 produits.")
        return value

    def create(self, validated_data):
        products = validated_data.pop('products')
        user = self.context['request'].user
        comparison = SavedComparison.objects.create(user=user, **validated_data)
        comparison.products.set(products)
        return comparison


# ============================================================
# ALERTES PRIX
# ============================================================
class PriceAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model  = PriceAlert
        fields = ['id', 'product', 'product_name', 'target_price', 'is_active', 'triggered_at', 'created_at']
        read_only_fields = ['id', 'triggered_at', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data['product']
        alert, created = PriceAlert.objects.update_or_create(
            user=user, product=product,
            defaults={
                'target_price': validated_data['target_price'],
                'is_active': True,
            }
        )
        return alert


# ============================================================
# NOTIFICATIONS
# ============================================================
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = NotificationModel
        fields = ['id', 'notification_type', 'title', 'message', 'is_read', 'created_at', 'read_at']
        read_only_fields = ['id', 'created_at', 'read_at']
