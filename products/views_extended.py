# ============================================================
#  products/views_extended.py  —  ViewSets pour Compare & Notifications
#  À AJOUTER aux views existantes
# ============================================================
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from .notifications import NotificationModel, NotificationService
from .compare import ProductComparer
from .serializers_extended import (
    NotificationSerializer, NotificationCreateSerializer,
    ComparisonRequestSerializer, ComparisonResultSerializer,
    FilterCriteriaSerializer
)
from .models import Product


# ============================================================
# VIEWSET - NOTIFICATIONS
# ============================================================
class NotificationViewSet(viewsets.ModelViewSet):
    """
    API pour gérer les notifications utilisateur.
    
    GET    /api/notifications/                 - Lister ses notifications
    GET    /api/notifications/{id}/            - Détail notification
    POST   /api/notifications/mark_as_read/    - Marquer comme lue
    DELETE /api/notifications/{id}/            - Supprimer notification
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourner seulement les notifications de l'utilisateur connecté."""
        return NotificationModel.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='unread')
    def unread(self, request):
        """Récupérer les notifications non lues."""
        unread = NotificationService.get_unread_notifications(request.user)
        serializer = self.get_serializer(unread, many=True)
        return Response({
            'count': unread.count(),
            'notifications': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marquer une notification comme lue."""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({
            'message': 'Notification marquée comme lue',
            'notification': NotificationSerializer(notification).data
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Marquer toutes les notifications comme lues."""
        unread = NotificationService.get_unread_notifications(request.user)
        count = unread.count()
        for notification in unread:
            notification.mark_as_read()
        return Response({
            'message': f'{count} notification(s) marquée(s) comme lue(s)'
        })
    
    @action(detail=False, methods=['post'])
    def create_notification(self, request):
        """Créer une nouvelle notification (admin/système)."""
        serializer = NotificationCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            notification = serializer.save()
            return Response(
                NotificationSerializer(notification).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# VIEWSET - COMPARE
# ============================================================
class CompareViewSet(viewsets.ViewSet):
    """
    API pour comparer les produits.
    
    POST /api/compare/compare/         - Comparer plusieurs produits
    POST /api/compare/filter/          - Filtrer et classer produits
    """
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], url_path='compare')
    def compare_products(self, request):
        """
        Comparer plusieurs produits.
        
        Body JSON:
        {
            "product_ids": [1, 2, 3]
        }
        """
        serializer = ComparisonRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        product_ids = serializer.validated_data['product_ids']
        result = ProductComparer.compare_multiple_products(product_ids)
        
        if 'error' in result:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='filter')
    def filter_products(self, request):
        """
        Filtrer les produits par critères.
        
        Body JSON:
        {
            "category": "smartphone",
            "min_price": 1000,
            "max_price": 10000,
            "min_rating": 4
        }
        """
        serializer = FilterCriteriaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        result = ProductComparer.filter_by_criteria(**serializer.validated_data)
        return Response({
            'count': len(result),
            'products': result
        }, status=status.HTTP_200_OK)
