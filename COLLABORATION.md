# 🤝 PLAN COLLABORATION - TechCompare

## Équipe
- **Personne 1 (Ami)** : Frontend React + Admin Backend + Compare Module + Notifications
- **Personne 2 (Vous)** : Scraping + AI Helper

---

## 📂 Structure Projet

```
COMPARISON/
├── backend/                          # Django Backend
│   ├── techcompare/                  # Settings
│   ├── products/                     # App Products
│   │   ├── models.py                 # Modèles (Product, Smartphone, Laptop)
│   │   ├── views.py                  # API Views
│   │   ├── serializers.py            # Serializers API
│   │   ├── ai_helper.py              # ← VOUS (AI)
│   │   ├── services.py               # Services métier
│   │   ├── filters.py                # Filtres
│   │   ├── pagination.py             # Pagination
│   │   ├── compare.py                # ← AMI (Compare)
│   │   └── notifications.py          # ← AMI (Notifications)
│   │
│   ├── management/commands/
│   │   └── sync_jumia.py             # ← VOUS (Scraping)
│   ├── auto_scraper.py               # ← VOUS (Scheduler)
│   ├── manage.py
│   ├── requirements.txt
│   └── db.sqlite3
│
└── frontend/                          # React Frontend (À créer)
    ├── src/
    ├── public/
    ├── package.json
    └── .env.local
```

---

## 🔄 Workflow Git

```bash
# Avant de coder
git pull origin main

# Créer branche pour sa tâche
git checkout -b feature/compare
# ou
git checkout -b feature/notifications

# Push après chaque milestone
git push origin feature/compare

# Pull request & merge sur main
```

---

## 🎯 Tâches Prioritaires

### PHASE 1 : Setup (15 min)
- [ ] Backend : `pip install -r requirements.txt`
- [ ] Backend : `python manage.py migrate`
- [ ] Backend : Tester `python manage.py runserver`
- [ ] **Ami** : Créer frontend avec React (Vite ou CRA)
- [ ] **Ami** : Créer `products/compare.py`
- [ ] **Ami** : Créer `products/notifications.py`
- [ ] **Vous** : Vérifier `auto_scraper.py` fonctionne
- [ ] **Vous** : Vérifier `ai_helper.py` fonctionne

### PHASE 2 : Intégration (30 min)
- [ ] Créer endpoints API pour compare
- [ ] Créer endpoints API pour notifications
- [ ] Frontend récupère données via API
- [ ] Tester flux complet

---

## 🛠️ Commandes Utiles

```bash
# Backend
python manage.py runserver                  # Démarrer serveur local
python manage.py createsuperuser            # Créer admin
python manage.py migrate                    # Appliquer migrations
python manage.py makemigrations             # Créer migrations
python auto_scraper.py                      # Scraper Jumia

# Frontend (après création)
npm start                                   # Démarrer React
npm run build                               # Build pour production
```

---

## 📡 API Endpoints (À Finaliser)

```
GET  /api/products/                         # Liste produits
GET  /api/products/{id}/                    # Détail produit
POST /api/compare/                          # Comparer produits
GET  /api/notifications/                    # Notifications
POST /api/notifications/                    # Créer notification
```

---

## ✨ Points Importants

1. **Git** : Toujours pull avant de coder, push souvent
2. **Branches** : Chacun sa branche, merge via PR
3. **Tests** : Tester localement avant de push
4. **Logs** : Console Django + React DevTools
5. **DB** : Synchroniser après migrations importantes

---

## 🎬 COMMENCER MAINTENANT

1. **Vous** : Lance `python manage.py runserver` pour vérifier le backend
2. **Ami** : Crée le dossier frontend avec React
3. **Tous** : Documentez vos endpoints/composants

Bonne chance ! 🚀
