import os
from typing import List, Dict

try:
    from google import genai
except Exception:
    genai = None

# Lecture de la clé depuis la variable d'environnement pour éviter d'écrire la clé en dur
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

def _make_client():
    if genai is None:
        return None
    if not GOOGLE_API_KEY:
        return None
    try:
        return genai.Client(api_key=GOOGLE_API_KEY)
    except Exception:
        return None


def conseiller_ia_best(products: List[Dict]) -> str:
    """
    Appelle l'API IA pour générer un court commentaire indiquant quel produit
    parmi la liste est le meilleur rapport qualité/prix. Si l'API n'est pas
    disponible, retourne un avis simple basé sur heuristique locale.
    """
    # Construire un prompt lisible pour l'IA
    lines = [
        "Tu es un expert en technologie pour un site e-commerce marocain.",
        "Compare ces produits et indique en une phrase lequel offre le meilleur rapport qualité/prix",
        "Fais une réponse concise et neutre.",
        "Produits :",
    ]
    for i, p in enumerate(products, start=1):
        name = p.get('name', 'Produit')
        price = p.get('price', 'N/A')
        ram = p.get('specs', {}).get('ram_gb') if isinstance(p.get('specs'), dict) else p.get('ram')
        storage = p.get('specs', {}).get('storage_gb') if isinstance(p.get('specs'), dict) else p.get('stockage')
        lines.append(f"Produit {i}: {name} — Prix: {price} Dhs — RAM: {ram} Go — Stockage: {storage} Go")

    prompt = "\n".join(lines)

    client = _make_client()
    if client:
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            # certains SDK renvoient .text ou .content
            return getattr(response, 'text', None) or getattr(response, 'content', None) or str(response)
        except Exception:
            # fallback to heuristic below
            pass

    # Heuristique simple : meilleur rapport RAM/prix, puis stockage/prix
    best = None
    best_score = float('inf')
    for p in products:
        price = None
        try:
            price = float(p.get('price') or 0)
        except Exception:
            price = 0.0
        ram = None
        if isinstance(p.get('specs'), dict):
            ram = p['specs'].get('ram_gb')
            storage = p['specs'].get('storage_gb')
        else:
            ram = p.get('ram')
            storage = p.get('stockage')
        ram = ram or 0
        storage = storage or 0
        score = price / max(1, ram) if ram else price / max(1, storage)
        if score < best_score:
            best_score = score
            best = p

    if best:
        name = best.get('name', 'Produit')
        price = best.get('price', 'N/A')
        return f"Meilleur rapport qualité/prix estimé: {name} à {price} Dhs."
    return "Aucun produit valide fourni."