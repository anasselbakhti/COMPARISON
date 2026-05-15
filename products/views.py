# ============================================================
#  products/views.py  —  Personne 1
#  Vues : Register, Login, Profil, Favoris, Produits
# ============================================================
from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Smartphone, Laptop, UserProfile, Favorite, Review, SavedComparison, PriceAlert
from .notifications import NotificationModel, NotificationService
from .serializers import (
    RegisterSerializer, UserSerializer, UserProfileSerializer,
    FavoriteSerializer, ProductSerializer, SmartphoneSerializer, LaptopSerializer,
    ReviewSerializer, SavedComparisonSerializer, PriceAlertSerializer, NotificationSerializer
)
from .filters import ProductFilter, SmartphoneFilter, LaptopFilter
from .scrapers.phone_detail import get_phone_specs
from .scrapers.laptop_detail import get_laptop_specs
from django.core.cache import cache


# ============================================================
# 1. INSCRIPTION — POST /api/auth/register/
# ============================================================
class RegisterView(generics.CreateAPIView):
    """
    Accessible sans token.
    Crée un User + UserProfile automatiquement.
    """
    queryset           = User.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Génère les tokens JWT directement après inscription
        refresh = RefreshToken.for_user(user)
        return Response({
            'message'      : 'Compte créé avec succès.',
            'user'         : UserSerializer(user).data,
            'access_token' : str(refresh.access_token),
            'refresh_token': str(refresh),
        }, status=status.HTTP_201_CREATED)


# ============================================================
# 2. CONNEXION — POST /api/auth/login/
# ============================================================
class LoginView(APIView):
    """
    Reçoit username + password, retourne les tokens JWT.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Username et password requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {'error': 'Identifiants incorrects.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'Compte désactivé.'},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'message'      : f'Bienvenue {user.username} !',
            'user'         : UserSerializer(user).data,
            'access_token' : str(refresh.access_token),
            'refresh_token': str(refresh),
        })


# ============================================================
# 3. DÉCONNEXION — POST /api/auth/logout/
# ============================================================
class LogoutView(APIView):
    """
    Invalide le refresh token (blacklist).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Déconnexion réussie.'})
        except Exception:
            return Response(
                {'error': 'Token invalide.'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================
# 4. PROFIL — GET/PUT /api/auth/profile/
# ============================================================
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Voir et modifier son propre profil.
    Nécessite d'être connecté (token JWT).
    """
    serializer_class   = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retourne uniquement le profil de l'utilisateur connecté
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


# ============================================================
# 5. FAVORIS — GET/POST/DELETE /api/favorites/
# ============================================================
class FavoriteViewSet(viewsets.ModelViewSet):
    """
    GET    /api/favorites/       → liste mes favoris
    POST   /api/favorites/       → ajouter un favori  {product_id: 3}
    DELETE /api/favorites/{id}/  → supprimer un favori
    """
    serializer_class   = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Chaque user ne voit QUE ses propres favoris
        return Favorite.objects.filter(
            user=self.request.user
        ).select_related('product')

    def perform_create(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Produit retiré des favoris.'},
            status=status.HTTP_200_OK
        )


# ============================================================
# 6. PRODUITS — GET /api/products/ /api/smartphones/ /api/laptops/
# ============================================================
class ProductViewSet(viewsets.ModelViewSet):
    queryset           = Product.objects.all()
    serializer_class   = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class    = ProductFilter
    search_fields      = ['name', 'brand']
    ordering_fields    = ['price', 'updated_at']
    ordering           = ['-updated_at']


class SmartphoneViewSet(viewsets.ModelViewSet):
    queryset           = Smartphone.objects.all()
    serializer_class   = SmartphoneSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class    = SmartphoneFilter
    search_fields      = ['name', 'brand', 'os']
    ordering_fields    = ['price', 'ram_gb', 'battery_mah']
    ordering           = ['-updated_at']

    @action(detail=True, methods=['post', 'get'])
    def fetch_details(self, request, pk=None):
        """Appel on-demand du scraper de détail pour enrichir le smartphone.

        GET/POST /api/smartphones/{id}/fetch_details/
        - Si les détails existent déjà et sont récents, retourne l'objet.
        - Sinon lance `get_phone_specs(source_url)`, met à jour l'objet et renvoie les données.
        """
        instance = self.get_object()

        # Vérifier cache simple pour éviter de scrapper trop souvent
        cache_key = f"product_details_sm_{instance.id}"
        cached = cache.get(cache_key)
        if cached:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        url = instance.source_url
        if not url:
            return Response({'error': 'Aucune source_url disponible pour ce produit.'}, status=400)

        try:
            details = get_phone_specs(url)
            if isinstance(details, dict):
                # Mettre à jour les champs si présents
                if details.get('battery_mah'):
                    instance.battery_mah = details.get('battery_mah')
                if details.get('camera_mp'):
                    instance.camera_mp = details.get('camera_mp')
                if details.get('release_year'):
                    instance.release_year = details.get('release_year')
                # Sauvegarde
                instance.save()
                cache.set(cache_key, True, timeout=60 * 60)  # 1 heure
        except Exception as e:
            return Response({'error': f'Erreur pendant le scraping: {e}'}, status=500)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class LaptopViewSet(viewsets.ModelViewSet):
    queryset           = Laptop.objects.all()
    serializer_class   = LaptopSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class    = LaptopFilter
    search_fields      = ['name', 'brand', 'cpu']
    ordering_fields    = ['price', 'ram_gb', 'weight_kg']
    ordering           = ['-updated_at']

    @action(detail=True, methods=['post', 'get'])
    def fetch_details(self, request, pk=None):
        """Scrape les détails d'un laptop à la demande et met à jour l'objet en BD."""
        instance = self.get_object()

        cache_key = f"product_details_lp_{instance.id}"
        if cache.get(cache_key):
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        url = instance.source_url
        if not url:
            return Response({'error': 'Aucune source_url disponible pour ce produit.'}, status=400)

        try:
            details = get_laptop_specs(url)
            if isinstance(details, dict):
                if details.get('battery_wh'):
                    instance.battery_wh = details.get('battery_wh')
                if details.get('weight_kg'):
                    instance.weight_kg = details.get('weight_kg')
                if details.get('release_year'):
                    instance.release_year = details.get('release_year')
                instance.save()
                cache.set(cache_key, True, timeout=60 * 60)
        except Exception as e:
            return Response({'error': f'Erreur pendant le scraping: {e}'}, status=500)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# ============================================================
# AVIS & NOTATION — GET/POST /api/reviews/
# ============================================================
class ReviewViewSet(viewsets.ModelViewSet):
    """
    GET    /api/reviews/?product=<id>  → liste les avis d'un produit
    POST   /api/reviews/               → soumettre un avis (auth requis)
    DELETE /api/reviews/<id>/          → supprimer son avis
    """
    serializer_class   = ReviewSerializer
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['product']
    ordering_fields    = ['created_at', 'rating']
    ordering           = ['-created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Review.objects.select_related('user', 'product').all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({'error': 'Vous ne pouvez supprimer que vos propres avis.'},
                            status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({'message': 'Avis supprimé.'}, status=status.HTTP_200_OK)


# ============================================================
# COMPARAISONS SAUVEGARDÉES — GET/POST /api/saved-comparisons/
# ============================================================
class SavedComparisonViewSet(viewsets.ModelViewSet):
    """
    GET    /api/saved-comparisons/       → mes comparaisons sauvegardées
    POST   /api/saved-comparisons/       → sauvegarder une comparaison
    DELETE /api/saved-comparisons/<id>/  → supprimer une comparaison
    """
    serializer_class   = SavedComparisonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedComparison.objects.filter(
            user=self.request.user
        ).prefetch_related('products')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Comparaison supprimée.'}, status=status.HTTP_200_OK)


# ============================================================
# ALERTES PRIX — GET/POST /api/alerts/
# ============================================================
class PriceAlertViewSet(viewsets.ModelViewSet):
    """
    GET    /api/alerts/       → mes alertes actives
    POST   /api/alerts/       → créer une alerte {product, target_price}
    DELETE /api/alerts/<id>/  → supprimer une alerte
    """
    serializer_class   = PriceAlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PriceAlert.objects.filter(user=self.request.user).select_related('product')

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """POST /api/alerts/<id>/toggle/ → activer/désactiver une alerte"""
        alert = self.get_object()
        alert.is_active = not alert.is_active
        alert.save()
        state = "activée" if alert.is_active else "désactivée"
        return Response({'message': f'Alerte {state}.', 'is_active': alert.is_active})


# ============================================================
# NOTIFICATIONS — GET /api/notifications/
# ============================================================
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/notifications/            → mes notifications
    GET /api/notifications/unread/     → notifications non lues
    POST /api/notifications/<id>/read/ → marquer comme lue
    """
    serializer_class   = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationModel.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """GET /api/notifications/unread/"""
        qs = NotificationService.get_unread_notifications(request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        """POST /api/notifications/<id>/read/ — marquer comme lue"""
        notif = self.get_object()
        notif.mark_as_read()
        return Response({'message': 'Notification marquée comme lue.'})

    @action(detail=False, methods=['post'])
    def read_all(self, request):
        """POST /api/notifications/read_all/ — tout marquer comme lu"""
        NotificationModel.objects.filter(user=request.user, is_read=False).update(
            is_read=True
        )
        return Response({'message': 'Toutes les notifications marquées comme lues.'})


# ============================================================
#  IA — Endpoint pour générer un court commentaire comparatif
# ============================================================
class AICompareView(APIView):
    """
    POST /api/ai/compare/  -> { products: [ {name, price, specs, ...}, ... ] }
    Retourne { comment: "..." }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        products = request.data.get('products')
        if not products or not isinstance(products, list):
            return Response({'error': 'Le champ "products" (liste) est requis.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from .ai_helper import conseiller_ia_best
        except Exception as e:
            return Response({'error': f'Impossible d\'importer ai_helper: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            comment = conseiller_ia_best(products)
            return Response({'comment': comment})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
