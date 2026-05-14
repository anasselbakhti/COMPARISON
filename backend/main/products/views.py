# ============================================================
#  products/views.py  —  Personne 1
#  Vues : Register, Login, Profil, Favoris, Produits
# ============================================================
from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Smartphone, Laptop, UserProfile, Favorite
from .serializers import (
    RegisterSerializer, UserSerializer, UserProfileSerializer,
    FavoriteSerializer, ProductSerializer, SmartphoneSerializer, LaptopSerializer
)
from .filters import ProductFilter, SmartphoneFilter, LaptopFilter


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


class LaptopViewSet(viewsets.ModelViewSet):
    queryset           = Laptop.objects.all()
    serializer_class   = LaptopSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class    = LaptopFilter
    search_fields      = ['name', 'brand', 'cpu']
    ordering_fields    = ['price', 'ram_gb', 'weight_kg']
    ordering           = ['-updated_at']