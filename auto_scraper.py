import schedule
import time
import os

def lancer_scraping_django():
    print("⏰ Lancement du processus de mise à jour automatique...")
    
    # Exécution de la commande Django
    os.system("python manage.py sync_jumia") 
    
    print("✅ Processus terminé avec succès ! La base de données a été mise à jour.")

# --- PLANIFICATION ---

# Pour le test : exécution toutes les minutes
schedule.every(1).minutes.do(lancer_scraping_django)

# Pour la production : exécution toutes les 6 heures (à activer après le test)
# schedule.every(6).hours.do(lancer_scraping_django)

print("🤖 Le robot est actif... En attente de l'heure d'exécution pour la commande Django.")

while True:
    schedule.run_pending()
    time.sleep(1)