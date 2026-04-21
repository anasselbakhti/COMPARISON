# ============================================================
#  products/models.py  —  Personne 1 : COMPLET
#  Modèles : Product, Smartphone, Laptop, UserProfile, Favoris
# ============================================================
from django.db import models
from django.contrib.auth.models import User


# ============================================================
# 1. PRODUIT (table parent)
# ============================================================
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('smartphone', 'Smartphone'),
        ('laptop',     'Laptop'),
    ]

    name       = models.CharField(max_length=200, verbose_name="Nom")
    brand      = models.CharField(max_length=100, verbose_name="Marque")
    category   = models.CharField(
                     max_length=20,
                     choices=CATEGORY_CHOICES,
                     verbose_name="Catégorie"
                 )
    price      = models.DecimalField(
                     max_digits=10,
                     decimal_places=2,
                     default=0.00,
                     verbose_name="Prix (MAD)"
                 )
    source_url = models.URLField(blank=True, verbose_name="URL source")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table            = 'tc_product'
        ordering            = ['-updated_at']
        verbose_name        = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return f"{self.brand} — {self.name}"

    def get_avg_rating(self):
        """Note moyenne — utilisée par Personne 2."""
        from django.db.models import Avg
        result = self.reviews.aggregate(avg=Avg('rating'))
        return round(result['avg'] or 0, 1)

    def get_specs(self):
        """Retourne les specs selon la catégorie."""
        if self.category == 'smartphone':
            try:
                s = self.smartphone
                return {
                    'os': s.os,
                    'ram_gb': s.ram_gb,
                    'storage_gb': s.storage_gb,
                    'camera_mp': s.camera_mp,
                    'battery_mah': s.battery_mah,
                    'screen_in': float(s.screen_in or 0),
                    'network': s.network,
                }
            except Smartphone.DoesNotExist:
                return {}
        elif self.category == 'laptop':
            try:
                l = self.laptop
                return {
                    'cpu': l.cpu,
                    'ram_gb': l.ram_gb,
                    'storage_gb': l.storage_gb,
                    'screen_in': float(l.screen_in or 0),
                    'gpu': l.gpu,
                    'battery_wh': l.battery_wh,
                    'weight_kg': float(l.weight_kg or 0),
                    'os': l.os,
                }
            except Laptop.DoesNotExist:
                return {}
        return {}


# ============================================================
# 2. SMARTPHONE (hérite de Product — MTI)
# ============================================================
class Smartphone(Product):
    NETWORK_CHOICES = [('3G', '3G'), ('4G', '4G'), ('5G', '5G')]

    os          = models.CharField(max_length=50,  default='')
    ram_gb      = models.SmallIntegerField(default=0)
    storage_gb  = models.SmallIntegerField(default=0)
    camera_mp   = models.SmallIntegerField(default=0)
    battery_mah = models.IntegerField(default=0)
    screen_in   = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    network     = models.CharField(max_length=10, choices=NETWORK_CHOICES, default='4G')

    class Meta:
        db_table            = 'tc_smartphone'
        verbose_name        = "Smartphone"
        verbose_name_plural = "Smartphones"

    def __str__(self):
        return f"{self.brand} {self.name} — {self.ram_gb}Go/{self.os}"


# ============================================================
# 3. LAPTOP (hérite de Product — MTI)
# ============================================================
class Laptop(Product):
    cpu        = models.CharField(max_length=100, default='')
    ram_gb     = models.SmallIntegerField(default=0)
    storage_gb = models.SmallIntegerField(default=0)
    screen_in  = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    gpu        = models.CharField(max_length=100, default='')
    battery_wh = models.SmallIntegerField(default=0)
    weight_kg  = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    os         = models.CharField(max_length=50, default='')

    class Meta:
        db_table            = 'tc_laptop'
        verbose_name        = "Laptop"
        verbose_name_plural = "Laptops"

    def __str__(self):
        return f"{self.brand} {self.name} — {self.cpu}"


# ============================================================
# 4. PROFIL UTILISATEUR (OneToOne avec User Django)
#    Étend le User de base avec des infos supplémentaires
# ============================================================
class UserProfile(models.Model):
    # OneToOneField : 1 User = 1 seul profil (relation 1-1)
    user       = models.OneToOneField(
                     User,
                     on_delete=models.CASCADE,   # si User supprimé → profil supprimé
                     related_name='profile',
                     verbose_name="Utilisateur"
                 )
    phone      = models.CharField(max_length=20, blank=True, default='')
    city       = models.CharField(max_length=100, blank=True, default='')
    avatar     = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table            = 'tc_userprofile'
        verbose_name        = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"Profil de {self.user.username}"


# ============================================================
# 5. FAVORIS (ManyToMany User <-> Product)
#    Un utilisateur peut avoir plusieurs produits en favoris
#    Un produit peut être dans les favoris de plusieurs users
# ============================================================
class Favorite(models.Model):
    # ForeignKey : plusieurs favoris peuvent appartenir au même user
    user       = models.ForeignKey(
                     User,
                     on_delete=models.CASCADE,
                     related_name='favorites',
                     verbose_name="Utilisateur"
                 )
    # ForeignKey : plusieurs users peuvent mettre le même produit en favori
    product    = models.ForeignKey(
                     Product,
                     on_delete=models.CASCADE,
                     related_name='favorited_by',
                     verbose_name="Produit"
                 )
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table            = 'tc_favorite'
        # Un user ne peut pas mettre le même produit en favori 2 fois
        unique_together     = ('user', 'product')
        ordering            = ['-added_at']
        verbose_name        = "Favori"
        verbose_name_plural = "Favoris"

    def __str__(self):
        return f"{self.user.username} → {self.product.name}"