# ============================================================
#  products/notifications.py  —  Personne 1 (Ami)
#  Service de notifications pour les alertes utilisateurs
# ============================================================
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class NotificationModel(models.Model):
    """
    Modèle pour stocker les notifications.
    """
    NOTIFICATION_TYPES = [
        ('price_drop', 'Baisse de prix'),
        ('new_product', 'Nouveau produit'),
        ('comparison', 'Résultat comparaison'),
        ('restock', 'Produit en stock'),
        ('system', 'Message système'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='system'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'tc_notification'
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Marquer la notification comme lue."""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class NotificationService:
    """
    Service pour gérer les notifications utilisateurs.
    """
    
    @staticmethod
    def create_notification(user, notification_type, title, message):
        """
        Crée une nouvelle notification pour un utilisateur.
        """
        return NotificationModel.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message
        )
    
    @staticmethod
    def notify_price_drop(product, old_price, new_price):
        """
        Notifie tous les utilisateurs qui ont ce produit en favoris
        si le prix a baissé.
        """
        from .models import Favorite
        
        favorites = Favorite.objects.filter(product=product).select_related('user')
        price_reduction = float(old_price - new_price)
        percentage = (price_reduction / float(old_price) * 100) if old_price > 0 else 0
        
        for favorite in favorites:
            NotificationService.create_notification(
                user=favorite.user,
                notification_type='price_drop',
                title=f'Baisse de prix : {product.name}',
                message=f'Prix réduit de {old_price} à {new_price} MAD (- {percentage:.1f}%)'
            )
    
    @staticmethod
    def notify_new_product(product, interested_users):
        """
        Notifie les utilisateurs intéressés qu'un nouveau produit a été ajouté.
        """
        for user in interested_users:
            NotificationService.create_notification(
                user=user,
                notification_type='new_product',
                title=f'Nouveau produit : {product.name}',
                message=f'{product.brand} - {product.category} disponible à {product.price} MAD'
            )
    
    @staticmethod
    def get_unread_notifications(user):
        """
        Récupère les notifications non lues d'un utilisateur.
        """
        return NotificationModel.objects.filter(user=user, is_read=False).order_by('-created_at')
    
    @staticmethod
    def get_all_notifications(user, days=30):
        """
        Récupère toutes les notifications d'un utilisateur (derniers N jours).
        """
        start_date = timezone.now() - timedelta(days=days)
        return NotificationModel.objects.filter(
            user=user,
            created_at__gte=start_date
        ).order_by('-created_at')
    
    @staticmethod
    def delete_old_notifications(days=90):
        """
        Supprime les notifications plus anciennes que N jours.
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = NotificationModel.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        return deleted_count
