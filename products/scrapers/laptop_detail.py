import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def get_laptop_specs(url):
    """Va chercher les détails profonds d'un laptop"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    specs = {'battery_wh': 0, 'weight_kg': 0.0, 'release_year': None}
    
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            text = soup.select_one('div.markup').get_text() if soup.select_one('div.markup') else ""
            
            # Extraction du poids (ex: 1.5 kg)
            weight = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kilogrammes)', text, re.I)
            # Extraction batterie (ex: 42 Wh)
            bat = re.search(r'(\d+)\s*Wh', text, re.I)
            # Recherche d'une année de sortie
            year_match = re.search(r"\b(20\d{2})\b", text)
            if year_match:
                try:
                    year_val = int(year_match.group(1))
                    current = datetime.now().year
                    if 2000 <= year_val <= current + 1:
                        specs['release_year'] = year_val
                except Exception:
                    pass
            
            if weight: specs['weight_kg'] = float(weight.group(1))
            if bat: specs['battery_wh'] = int(bat.group(1))
    except Exception as e:
        print(f"Erreur détail laptop: {e}")
        
    return specs