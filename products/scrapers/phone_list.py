import requests
from bs4 import BeautifulSoup
import re

def extract_specs_from_name(name):
    specs = {'ram_gb': 0, 'storage_gb': 0, 'screen_in': None, 'network': '4G', 'os': 'Android'}
    ram_match = re.search(r'(\d+)\s*(GB|Go|G)\s*RAM', name, re.IGNORECASE)
    if ram_match: specs['ram_gb'] = int(ram_match.group(1))
    storage_match = re.search(r'(32|64|128|256|512|1024)\s*(GB|Go|G)', name, re.IGNORECASE)
    if storage_match: specs['storage_gb'] = int(storage_match.group(1))
    screen_match = re.search(r'(\d+\.\d+)\s*(["”]|inch)', name, re.IGNORECASE)
    if screen_match: specs['screen_in'] = float(screen_match.group(1))
    if '5G' in name.upper(): specs['network'] = '5G'
    if 'IPHONE' in name.upper() or 'APPLE' in name.upper(): specs['os'] = 'iOS'
    return specs

def scrape_phones_catalog():
    url = "https://www.jumia.ma/smartphones/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    smartphones = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        for art in soup.find_all('article', class_='prd'):
            try:
                name = art.find('h3', class_='name').text.strip()
                price_raw = art.find('div', class_='prc').text.replace('Dhs', '').replace(',', '').replace(' ', '').strip()
                core_data = art.find('a', class_='core')
                specs = extract_specs_from_name(name)
                smartphones.append({
                    "name": name, "brand": core_data.get('data-brand', name.split()[0]),
                    "price": float(price_raw), "source_url": "https://www.jumia.ma" + core_data['href'], **specs
                })
            except: continue
    return smartphones