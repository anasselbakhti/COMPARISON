from .models import Smartphone, Laptop
from .scrapers.phone_detail import get_phone_specs
from .scrapers.laptop_detail import get_laptop_specs

def enrich_product_details(product_id, category):
    """
    Cette fonction prend un produit incomplet, va scraper sa page Jumia,
    et remplit les colonnes vides dans MySQL.
    """
    if category == 'smartphone':
        product = Smartphone.objects.get(id=product_id)
        # On appelle ton script phone_detail.py avec l'URL sauvegardée
        extra_specs = get_phone_specs(product.source_url)
        
        # On met à jour les champs manquants
        product.battery_mah = extra_specs.get('battery_mah', product.battery_mah)
        product.camera_mp = extra_specs.get('camera_mp', product.camera_mp)
        # Si la RAM était à 0 (non trouvée dans le titre), on la met à jour
        if product.ram_gb == 0:
            product.ram_gb = extra_specs.get('ram_gb', 0)
        
        product.save()
        return product

    elif category == 'laptop':
        product = Laptop.objects.get(id=product_id)
        # On appelle ton script laptop_detail.py
        extra_specs = get_laptop_specs(product.source_url)
        
        product.weight_kg = extra_specs.get('weight_kg', product.weight_kg)
        product.battery_wh = extra_specs.get('battery_wh', product.battery_wh)
        
        # Si le CPU était "Inconnu", on essaye de le récupérer en détail
        if product.cpu == "Inconnu":
            product.cpu = extra_specs.get('cpu', "Inconnu")
            
        product.save()
        return product