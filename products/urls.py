# ============================================================
#  products/urls.py  —  Personne 1
# ============================================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, LoginView, LogoutView, ProfileView,
    FavoriteViewSet, ProductViewSet, SmartphoneViewSet, LaptopViewSet,
    ReviewViewSet, SavedComparisonViewSet, PriceAlertViewSet, NotificationViewSet
)
from .views import AICompareView

router = DefaultRouter()
router.register(r'products',           ProductViewSet,          basename='product')
router.register(r'smartphones',        SmartphoneViewSet,       basename='smartphone')
router.register(r'laptops',            LaptopViewSet,           basename='laptop')
router.register(r'favorites',          FavoriteViewSet,         basename='favorite')
router.register(r'reviews',            ReviewViewSet,           basename='review')
router.register(r'saved-comparisons',  SavedComparisonViewSet,  basename='saved-comparison')
router.register(r'alerts',             PriceAlertViewSet,       basename='alert')
router.register(r'notifications',      NotificationViewSet,     basename='notification')

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(),     name='register'),
    path('auth/login/',    LoginView.as_view(),         name='login'),
    path('auth/logout/',   LogoutView.as_view(),        name='logout'),
    path('auth/refresh/',  TokenRefreshView.as_view(),  name='token_refresh'),
    path('auth/profile/',  ProfileView.as_view(),       name='profile'),

    # Produits + Favoris + Reviews + Comparaisons + Alertes + Notifications
    path('', include(router.urls)),
    # IA
    path('ai/compare/', AICompareView.as_view(), name='ai_compare'),
]