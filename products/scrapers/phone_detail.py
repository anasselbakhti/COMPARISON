import requests
from bs4 import BeautifulSoup
import re

def get_phone_specs(url):
    """Va chercher les détails profonds d'un smartphone"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    specs = {'battery_mah': 0, 'camera_mp': 0}
    
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            # Jumia stocke les specs dans la div 'markup'
            text = soup.select_one('div.markup').get_text() if soup.select_one('div.markup') else ""
            
            # Recherche via expressions régulières (Regex)
            bat = re.search(r'(\d{4,5})\s*mAh', text, re.I)
            cam = re.search(r'(\d+)\s*(?:MP|Mégapixels)', text, re.I)
            
            if bat: specs['battery_mah'] = int(bat.group(1))
            if cam: specs['camera_mp'] = int(cam.group(1))
    except Exception as e:
        print(f"Erreur détail phone: {e}")
        
    return specs