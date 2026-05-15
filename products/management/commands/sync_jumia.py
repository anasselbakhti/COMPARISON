from django.core.management.base import BaseCommand
from products.models import Smartphone, Laptop
from products.scrapers.phone_list import scrape_phones_catalog
from products.scrapers.laptop_list import scrape_laptops_catalog
from products.validation import DataValidator, ValidationError, ScrapingStats
from products.scrapers.phone_detail import get_phone_specs
from products.scrapers.laptop_detail import get_laptop_specs
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Scrape Jumia et synchronise la base de données avec validation robuste"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("--- DÉBUT DE LA SYNCHRONISATION ---"))
        
        stats = ScrapingStats()

        # ==========================================
        # 1. SMARTPHONES
        # ==========================================
        self.stdout.write("\n📱 Scraping des smartphones en cours...")
        phones_data = scrape_phones_catalog()
        self.stdout.write(f"  {len(phones_data)} smartphones trouvés")
        
        for item in phones_data:
            stats.total_processed += 1
            try:
                # Enrichir avec détails depuis la page produit (batterie, caméra, année)
                try:
                    details = get_phone_specs(item.get('source_url', ''))
                    if isinstance(details, dict):
                        item.update(details)
                except Exception:
                    # Ignore les erreurs de détail; on continue avec les données existantes
                    pass

                # Validation stricte des données
                validated_data = DataValidator.validate_smartphone_data(item)
                
                # Détection des anomalies
                anomalies = DataValidator.detect_anomalies(validated_data, 'smartphone')
                if anomalies:
                    stats.anomalies_detected += len(anomalies)
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠️  Anomalie: {item['name']}")
                    )
                    for anomaly in anomalies:
                        self.stdout.write(f"      • {anomaly}")
                
                # Sauvegarde en BD
                obj, created = Smartphone.objects.update_or_create(
                    source_url=validated_data['source_url'],
                    defaults={
                        'name': validated_data['name'],
                        'brand': validated_data['brand'],
                        'price': validated_data['price'],
                        'category': validated_data['category'],
                        'ram_gb': validated_data['ram_gb'],
                        'storage_gb': validated_data['storage_gb'],
                        'screen_in': validated_data['screen_in'],
                        'network': validated_data['network'],
                        'os': validated_data['os'],
                        'camera_mp': validated_data.get('camera_mp', 0),
                        'battery_mah': validated_data.get('battery_mah', 0),
                        'release_year': validated_data['release_year'],
                    }
                )
                status = "✨ Créé" if created else "🔄 Mis à jour"
                self.stdout.write(f"  [{status}] {obj.name}")
                stats.successfully_validated += 1
                
            except ValidationError as e:
                stats.add_error(item.get('name', 'Inconnu'), str(e))
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Smartphone rejeté: {item.get('name', 'Inconnu')}")
                )
                self.stdout.write(f"     Raison: {e}")
            except Exception as e:
                stats.add_error(item.get('name', 'Inconnu'), str(e))
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Erreur inattendue: {item.get('name', 'Inconnu')}")
                )
                self.stdout.write(f"     {str(e)}")

        # ==========================================
        # 2. LAPTOPS
        # ==========================================
        self.stdout.write("\n💻 Scraping des laptops en cours...")
        laptops_data = scrape_laptops_catalog()
        self.stdout.write(f"  {len(laptops_data)} laptops trouvés")
        
        for item in laptops_data:
            stats.total_processed += 1
            try:
                # Enrichir avec détails depuis la page produit (poids, batterie, année)
                try:
                    details = get_laptop_specs(item.get('source_url', ''))
                    if isinstance(details, dict):
                        item.update(details)
                except Exception:
                    pass

                # Validation stricte des données
                validated_data = DataValidator.validate_laptop_data(item)
                
                # Détection des anomalies
                anomalies = DataValidator.detect_anomalies(validated_data, 'laptop')
                if anomalies:
                    stats.anomalies_detected += len(anomalies)
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠️  Anomalie: {item['name']}")
                    )
                    for anomaly in anomalies:
                        self.stdout.write(f"      • {anomaly}")
                
                # Sauvegarde en BD
                obj, created = Laptop.objects.update_or_create(
                    source_url=validated_data['source_url'],
                    defaults={
                        'name': validated_data['name'],
                        'brand': validated_data['brand'],
                        'price': validated_data['price'],
                        'category': validated_data['category'],
                        'cpu': validated_data['cpu'],
                        'ram_gb': validated_data['ram_gb'],
                        'storage_gb': validated_data['storage_gb'],
                        'screen_in': validated_data['screen_in'],
                        'gpu': validated_data['gpu'],
                        'os': validated_data['os'],
                        'battery_wh': validated_data['battery_wh'],
                        'weight_kg': validated_data['weight_kg'],
                        'release_year': validated_data['release_year'],
                    }
                )
                status = "✨ Créé" if created else "🔄 Mis à jour"
                self.stdout.write(f"  [{status}] {obj.name}")
                stats.successfully_validated += 1
                
            except ValidationError as e:
                stats.add_error(item.get('name', 'Inconnu'), str(e))
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Laptop rejeté: {item.get('name', 'Inconnu')}")
                )
                self.stdout.write(f"     Raison: {e}")
            except Exception as e:
                stats.add_error(item.get('name', 'Inconnu'), str(e))
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Erreur inattendue: {item.get('name', 'Inconnu')}")
                )
                self.stdout.write(f"     {str(e)}")

        # ==========================================
        # 3. RÉSUMÉ
        # ==========================================
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("📊 RÉSUMÉ DE LA SYNCHRONISATION"))
        self.stdout.write("="*60)
        self.stdout.write(f"Total traité:        {stats.total_processed}")
        self.stdout.write(self.style.SUCCESS(f"Valides et sauvegardés: {stats.successfully_validated}"))
        self.stdout.write(self.style.ERROR(f"Erreurs de validation: {stats.validation_errors}"))
        self.stdout.write(self.style.WARNING(f"Anomalies détectées:   {stats.anomalies_detected}"))
        
        if stats.errors:
            self.stdout.write("\n⚠️  Premiers erreurs détaillées:")
            for error in stats.errors[:5]:
                self.stdout.write(f"  • {error['item']}: {error['error']}")
            if len(stats.errors) > 5:
                self.stdout.write(f"  ... et {len(stats.errors) - 5} autres")
        
        self.stdout.write("="*60)
        self.stdout.write(self.style.SUCCESS("✅ SYNCHRONISATION TERMINÉE\n"))