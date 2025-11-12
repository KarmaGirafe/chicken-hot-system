# 🍔 Chicken Hot Dreux - Système de Commandes IA

Système complet de prise de commandes par téléphone avec IA pour le restaurant Chicken Hot Dreux.

## 📦 Structure du Projet

```
chicken-hot-system/
├── server.py                  # Serveur Flask principal
├── order_analyzer.py          # Analyseur IA avec OpenAI
├── requirements.txt           # Dépendances Python
├── Dockerfile                 # Configuration Docker
├── .dockerignore             # Fichiers à ignorer par Docker
├── .gitignore                # Fichiers à ignorer par Git
├── static/
│   ├── index.html            # Interface web restaurant
│   ├── style.css             # Styles CSS
│   └── app.js                # Logique JavaScript
└── firebase-key.json         # Clés Firebase (à créer)
```

## 🚀 Étape 1 : Créer Firebase

### 1.1 - Créer le projet
1. Va sur https://console.firebase.google.com
2. "Ajouter un projet" → Nom: `chicken-hot-dreux`
3. Désactive Google Analytics
4. Créer

### 1.2 - Créer la Realtime Database
1. Menu → "Realtime Database"
2. "Créer une base de données"
3. Région: `europe-west1`
4. Mode: "Test" (pour commencer)
5. Activer

**Copie l'URL** (ex: `https://chicken-hot-xxx.firebaseio.com`)

### 1.3 - Télécharger les clés
1. Paramètres (roue crantée) → "Comptes de service"
2. "Générer une nouvelle clé privée"
3. Télécharge le JSON
4. Renomme en `firebase-key.json`
5. Place dans le dossier du projet

## 🔧 Étape 2 : Préparer Google Cloud Run

### 2.1 - Créer compte Google Cloud
1. Va sur https://console.cloud.google.com
2. Active l'essai gratuit (300€ de crédits)
3. Crée un projet: `chicken-hot-system`

### 2.2 - Activer les APIs
1. Menu → "APIs et services" → "Bibliothèque"
2. Active ces APIs:
   - ✅ Cloud Run API
   - ✅ Cloud Build API
   - ✅ Container Registry API

## 📂 Étape 3 : Organiser les Fichiers

### 3.1 - Créer la structure
```bash
mkdir chicken-hot-system
cd chicken-hot-system
mkdir static
```

### 3.2 - Placer les fichiers
- `server.py` → Racine
- `order_analyzer.py` → Racine
- `requirements.txt` → Racine
- `Dockerfile` → Racine
- `.dockerignore` → Racine
- `.gitignore` → Racine
- `static_index.html` → Renommer en `static/index.html`
- `static_style.css` → Renommer en `static/style.css`
- `static_app.js` → Renommer en `static/app.js`
- `firebase-key.json` → Racine (après l'avoir téléchargé)

## 🌐 Étape 4 : Déployer sur Cloud Run

### Option A : Via la Console (Le plus simple)

1. **Va sur https://console.cloud.google.com/run**
2. **Create Service**
3. **Configuration:**
   - Source: "Continuously deploy from a repository" (setup GitHub)
   - Region: `europe-west1` (Paris)
   - Authentication: "Allow unauthenticated invocations" ✅
   - CPU allocation: "CPU is only allocated during request processing"
   - Min instances: 0
   - Max instances: 10

4. **Environment Variables** (très important !):
   ```
   OPENAI_API_KEY=sk-proj-xxxxxxxxxx
   FIREBASE_URL=https://ton-projet.firebaseio.com
   FIREBASE_KEY={"type":"service_account","project_id":"..."}
   ```
   
   Pour FIREBASE_KEY:
   - Ouvre `firebase-key.json`
   - Copie TOUT le contenu
   - Colle-le tel quel dans la variable

5. **Deploy**

### Option B : Via gcloud CLI

```bash
# 1. Installer gcloud CLI
# https://cloud.google.com/sdk/docs/install

# 2. Se connecter
gcloud auth login
gcloud config set project chicken-hot-system

# 3. Build et Deploy
gcloud builds submit --tag gcr.io/chicken-hot-system/app

gcloud run deploy chicken-hot \
  --image gcr.io/chicken-hot-system/app \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=sk-xxx \
  --set-env-vars FIREBASE_URL=https://xxx.firebaseio.com \
  --set-env-vars FIREBASE_KEY='{"type":"service_account"...}'
```

## 🎯 Étape 5 : Configurer Retell

1. **Va dans ton dashboard Retell**
2. **Configure le webhook:**
   - URL: `https://ton-app-xxx.run.app/webhook/retell`
   - Method: POST

3. **Teste avec un appel !**

## 🖥️ Étape 6 : Utilisation au Restaurant

1. **Ouvre un navigateur** (Chrome, Firefox, Safari)
2. **Va sur:** `https://ton-app-xxx.run.app`
3. **Les commandes apparaissent automatiquement !**

## 💰 Coûts Mensuels

Pour 1500 appels/mois:
- **Google Cloud Run:** GRATUIT (sous 2M requêtes)
- **Firebase:** GRATUIT (sous 1GB)
- **OpenAI GPT-4o:** ~4,50€/mois

**Total: 4,50€/mois** 🎉

## 🔍 Test en Local

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Variables d'environnement
export OPENAI_API_KEY=sk-xxx
export FIREBASE_URL=https://xxx.firebaseio.com
# (firebase-key.json doit être dans le dossier)

# 3. Lancer
python server.py

# 4. Ouvrir
# http://localhost:5000
```

## 📝 Test du Webhook

Crée `test_webhook.json`:
```json
{
  "call": {
    "call_id": "test_123",
    "start_timestamp": 1762872681571,
    "duration_ms": 25000,
    "transcript": "Bonjour, je voudrais deux menus curry sur place s'il vous plaît"
  }
}
```

Test:
```bash
curl -X POST http://localhost:5000/webhook/retell \
  -H "Content-Type: application/json" \
  -d @test_webhook.json
```

## 🐛 Dépannage

### Erreur Firebase
- Vérifie que `firebase-key.json` est bien présent
- Vérifie que l'URL Firebase est correcte dans les variables d'env

### Erreur OpenAI
- Vérifie que ta clé API OpenAI est valide
- Vérifie que tu as du crédit sur ton compte OpenAI

### Erreur "Service not found"
- Vérifie que le service est bien déployé
- Regarde les logs: `gcloud run services logs read chicken-hot`

## 📱 Contact

Pour tout problème: akram@echolink.fr

## 📄 Licence

Propriété d'Echo Link - Tous droits réservés
"# chicken-hot-system" 
"# chicken-hot-system" 
