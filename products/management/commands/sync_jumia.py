from django.core.management.base import BaseCommand
from products.models import Smartphone, Laptop
from products.scrapers.phone_list import scrape_phones_catalog
from products.scrapers.laptop_list import scrape_laptops_catalog

class Command(BaseCommand):
    help = "Scrape Jumia et synchronise la base de données avec les specs"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("--- DÉBUT DE LA SYNCHRONISATION ---"))

        # ==========================================
        # 1. SMARTPHONES
        # ==========================================
        self.stdout.write("Scraping des smartphones en cours...")
        phones_data = scrape_phones_catalog()
        
        for item in phones_data:
            # update_or_create met à jour le produit s'il existe déjà (via source_url) ou le crée
            obj, created = Smartphone.objects.update_or_create(
                source_url=item['source_url'],
                defaults={
                    # Infos de base (Modèle Product)
                    'name': item['name'],
                    'brand': item.get('brand', 'Smartphone'),
                    'price': item['price'],
                    'category': 'smartphone',
                    
                    # Specs spécifiques (Modèle Smartphone) extraites par Regex
                    'ram_gb': item.get('ram_gb', 0),
                    'storage_gb': item.get('storage_gb', 0),
                    'screen_in': item.get('screen_in'),
                    'network': item.get('network', '4G'),
                    'os': item.get('os', 'Android'),
                }
            )
            status = "Créé" if created else "Mis à jour"
            self.stdout.write(f"  [{status}] {obj.name}")

        # ==========================================
        # 2. LAPTOPS
        # ==========================================
        self.stdout.write("\nScraping des laptops en cours...")
        laptops_data = scrape_laptops_catalog()
        
        for item in laptops_data:
            obj, created = Laptop.objects.update_or_create(
                source_url=item['source_url'],
                defaults={
                    # Infos de base (Modèle Product)
                    'name': item['name'],
                    'brand': item.get('brand', 'Laptop'),
                    'price': item['price'],
                    'category': 'laptop',
                    
                    # Specs spécifiques (Modèle Laptop) extraites par Regex
                    'cpu': item.get('cpu', 'Inconnu'),
                    'ram_gb': item.get('ram_gb', 0),
                    'storage_gb': item.get('storage_gb', 0),
                    'screen_in': item.get('screen_in'),
                    'gpu': item.get('gpu', 'Intégré'),
                    'os': item.get('os', 'FreeDOS'),
                }
            )
            status = "Créé" if created else "Mis à jour"
            self.stdout.write(f"  [{status}] {obj.name}")

        self.stdout.write(self.style.SUCCESS("\n--- SYNCHRONISATION TERMINÉE AVEC SUCCÈS ---"))