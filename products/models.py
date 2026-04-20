from django.db import models

class Product(models.Model):
    name        = models.CharField(max_length=200)
    brand       = models.CharField(max_length=100)
    category    = models.CharField(max_length=20)  # 'smartphone' ou 'laptop'
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    source_url  = models.URLField()
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.name}"


class Smartphone(Product):
    os          = models.CharField(max_length=50)
    ram_gb      = models.SmallIntegerField()
    storage_gb  = models.SmallIntegerField()
    camera_mp   = models.SmallIntegerField()
    battery_mah = models.IntegerField()

    def __str__(self):
        return f"Smartphone: {self.brand} {self.name}"


class Laptop(Product):
    cpu        = models.CharField(max_length=100)
    ram_gb     = models.SmallIntegerField()
    storage_gb = models.SmallIntegerField()
    screen_in  = models.DecimalField(max_digits=4, decimal_places=1)
    gpu        = models.CharField(max_length=100)

    def __str__(self):
        return f"Laptop: {self.brand} {self.name}"
