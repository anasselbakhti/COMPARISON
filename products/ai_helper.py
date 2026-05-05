from google import genai

# 1. Configuration (Remplace par ta vraie clé API)
GOOGLE_API_KEY = "AIzaSyCfK-A-HfaHddAZICxPrPMYcFhyNfkZgeY"

# Nouvelle façon de se connecter
client = genai.Client(api_key=GOOGLE_API_KEY)

def conseiller_ia(produit_A, produit_B):
    print("⏳ L'IA analyse les produits... Veuillez patienter.\n")
    
    # 2. Le "Prompt" (Les instructions)
    prompt = f"""
    Tu es un expert en technologie sur un site e-commerce marocain. 
    Compare ces deux produits de manière neutre, professionnelle et concise (maximum 4 phrases). 
    Dis lequel est le meilleur rapport qualité/prix.

    Produit A : {produit_A['name']} (Prix: {produit_A['price']} Dhs, RAM: {produit_A['ram']} Go, Stockage: {produit_A['stockage']} Go)
    Produit B : {produit_B['name']} (Prix: {produit_B['price']} Dhs, RAM: {produit_B['ram']} Go, Stockage: {produit_B['stockage']} Go)
    """

    # 3. Appel à l'IA (Nouvelle syntaxe)
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Erreur de connexion à l'IA : {e}"

# --- SIMULATION ---
tel_1 = {'name': 'Samsung Galaxy A16', 'price': 1990, 'ram': 4, 'stockage': 128}
tel_2 = {'name': 'XIAOMI Redmi Note 15', 'price': 2100, 'ram': 6, 'stockage': 128}

# On lance la fonction
avis = conseiller_ia(tel_1, tel_2)

print("🤖 L'avis de l'Expert IA :")
print("-" * 40)
print(avis)
print("-" * 40)