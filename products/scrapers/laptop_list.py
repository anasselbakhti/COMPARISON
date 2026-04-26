import requests
from bs4 import BeautifulSoup
import re

def extract_laptop_specs_from_name(name):
    specs = {'cpu': 'Inconnu', 'ram_gb': 0, 'storage_gb': 0, 'screen_in': None, 'gpu': 'Intégré', 'os': 'FreeDOS'}
    ram_match = re.search(r'(\d+)\s*(GB|Go|G)\s*RAM', name, re.IGNORECASE)
    if ram_match: specs['ram_gb'] = int(ram_match.group(1))
    storage_match = re.search(r'(\d+)\s*(TB|To|GB|Go)', name, re.IGNORECASE)
    if storage_match:
        val = int(storage_match.group(1))
        specs['storage_gb'] = val * 1024 if 'T' in storage_match.group(2).upper() else val
    cpu_match = re.search(r'(i[3579]|Ryzen\s?[3579]|Celeron|Pentium|M[123])', name, re.IGNORECASE)
    if cpu_match: specs['cpu'] = cpu_match.group(1).upper()
    return specs

def scrape_laptops_catalog():
    url = "https://www.jumia.ma/pc-portables/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    laptops = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        for art in soup.find_all('article', class_='prd'):
            try:
                name = art.find('h3', class_='name').text.strip()
                price_raw = art.find('div', class_='prc').text.replace('Dhs', '').replace(',', '').replace(' ', '').strip()
                specs = extract_laptop_specs_from_name(name)
                laptops.append({
                    "name": name, "brand": art.find('a', class_='core').get('data-brand', name.split()[0]),
                    "price": float(price_raw), "source_url": "https://www.jumia.ma" + art.find('a', class_='core')['href'], **specs
                })
            except: continue
    return laptops