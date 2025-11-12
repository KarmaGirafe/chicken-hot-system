# 🚀 GUIDE DE DÉPLOIEMENT ULTRA SIMPLE

## ✅ CE DONT TU AS BESOIN

1. Compte Google (Gmail)
2. Clé API OpenAI
3. 30 minutes de temps

---

## 📋 ÉTAPE PAR ÉTAPE

### ▶️ ÉTAPE 1 : FIREBASE (5 min)

1. **Va sur:** https://console.firebase.google.com
2. **Clique:** "Ajouter un projet"
3. **Nom:** `chicken-hot-dreux`
4. **Désactive** Google Analytics
5. **Clique:** "Créer le projet"

⏳ Attends que Firebase crée le projet...

6. **Dans le menu de gauche →** "Realtime Database"
7. **Clique:** "Créer une base de données"
8. **Région:** `europe-west1`
9. **Mode:** "Commencer en mode test"
10. **Clique:** "Activer"

✅ **COPIE L'URL** qui apparaît (ressemble à: `https://chicken-hot-xxx.firebaseio.com`)

11. **Clique sur la roue crantée** en haut à gauche
12. **"Paramètres du projet"**
13. **Onglet "Comptes de service"**
14. **Clique:** "Générer une nouvelle clé privée"
15. **Télécharge le fichier** (c'est un .json)

✅ **GARDE CE FICHIER** bien au chaud !

---

### ▶️ ÉTAPE 2 : GOOGLE CLOUD (5 min)

1. **Va sur:** https://console.cloud.google.com
2. **Clique:** "Essai gratuit" (en haut)
3. **Remplis le formulaire** (carte bancaire demandée mais RIEN ne sera débité)
4. **Valide**

5. **En haut, clique sur:** "Sélectionner un projet"
6. **Clique:** "Nouveau projet"
7. **Nom:** `chicken-hot-system`
8. **Clique:** "Créer"

⏳ Attends quelques secondes...

9. **Dans le menu ☰ (hamburger) →** "APIs et services" → "Bibliothèque"
10. **Cherche:** "Cloud Run API" → **ACTIVE**
11. **Cherche:** "Cloud Build API" → **ACTIVE**

✅ C'est bon pour Cloud !

---

### ▶️ ÉTAPE 3 : ORGANISER LES FICHIERS (10 min)

1. **Télécharge TOUS les fichiers** que je t'ai créés
2. **Crée un dossier:** `chicken-hot-system`
3. **À l'intérieur, crée un dossier:** `static`

4. **Place les fichiers comme ça:**

```
chicken-hot-system/
├── server.py
├── order_analyzer.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── firebase-key.json (le fichier que tu as téléchargé de Firebase)
└── static/
    ├── index.html (renomme static_index.html)
    ├── style.css (renomme static_style.css)
    └── app.js (renomme static_app.js)
```

**IMPORTANT:** Les fichiers `static_xxx` doivent être renommés et mis dans le dossier `static/`

---

### ▶️ ÉTAPE 4 : POUSSER SUR GITHUB (5 min)

1. **Va sur:** https://github.com
2. **Clique:** "New repository"
3. **Nom:** `chicken-hot-system`
4. **Private** ✅
5. **Clique:** "Create repository"

6. **Ouvre un terminal** dans ton dossier `chicken-hot-system`
7. **Tape ces commandes:**

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TON-USERNAME/chicken-hot-system.git
git push -u origin main
```

✅ Ton code est sur GitHub !

---

### ▶️ ÉTAPE 5 : DÉPLOYER SUR CLOUD RUN (10 min)

1. **Va sur:** https://console.cloud.google.com/run
2. **Clique:** "CREATE SERVICE"

3. **Configuration:**
   - ✅ "Continuously deploy from a repository (setup GitHub)"
   - **Clique:** "SET UP WITH CLOUD BUILD"
   - **Connecte ton GitHub**
   - **Sélectionne:** `chicken-hot-system`
   - **Branch:** `main`
   - **Build Type:** "Dockerfile"
   - **Source location:** `/Dockerfile`

4. **Service Settings:**
   - **Region:** `europe-west1`
   - **CPU allocation:** "CPU is only allocated during request processing"
   - **Autoscaling:** Min 0, Max 10
   - **Authentication:** ✅ "Allow unauthenticated invocations"

5. **VARIABLES D'ENVIRONNEMENT** (très important !) :

Clique sur "CONTAINER, VARIABLES & SECRETS, CONNECTIONS, SECURITY"

Ajoute ces 3 variables:

**Variable 1:**
- Name: `OPENAI_API_KEY`
- Value: `sk-proj-xxxxxxxxxx` (ta clé OpenAI)

**Variable 2:**
- Name: `FIREBASE_URL`
- Value: `https://chicken-hot-xxx.firebaseio.com` (l'URL que tu as copié)

**Variable 3:**
- Name: `FIREBASE_KEY`
- Value: Ouvre le fichier `firebase-key.json` avec un éditeur de texte, **COPIE TOUT** et colle ici

6. **Clique:** "CREATE"

⏳ **Attends 5-10 minutes** que ça build et déploie...

✅ **TU AS UNE URL !** Genre: `https://chicken-hot-xxx.run.app`

---

### ▶️ ÉTAPE 6 : CONFIGURER RETELL (2 min)

1. **Va dans ton dashboard Retell**
2. **Paramètres → Webhook**
3. **URL:** `https://chicken-hot-xxx.run.app/webhook/retell`
4. **Method:** POST
5. **Save**

---

### ▶️ ÉTAPE 7 : TESTER ! 🎉

**Option 1 : Interface Web**
1. Ouvre un navigateur
2. Va sur: `https://chicken-hot-xxx.run.app`
3. Tu verras l'interface vide

**Option 2 : Appel Test**
1. Utilise ton téléphone Retell
2. Passe un appel
3. Dis: "Bonjour, je voudrais un menu curry sur place"
4. Regarde l'interface web → LA COMMANDE APPARAÎT ! 🎉

---

## 🎊 C'EST FINI !

Tu as maintenant un système professionnel qui :
- ✅ Reçoit les appels Retell
- ✅ Analyse avec l'IA OpenAI
- ✅ Affiche les commandes en temps réel
- ✅ Calcule les prix automatiquement
- ✅ Coûte 4,50€/mois

---

## 🆘 BESOIN D'AIDE ?

### L'interface ne s'affiche pas
- Vérifie l'URL dans le navigateur
- Ouvre la console (F12) et regarde les erreurs

### Les commandes n'apparaissent pas
- Vérifie les variables d'environnement dans Cloud Run
- Vérifie l'URL du webhook dans Retell

### Erreur "Firebase initialization"
- Vérifie que FIREBASE_KEY est bien copié entièrement
- Vérifie que FIREBASE_URL est correct

### Voir les logs
```bash
gcloud run services logs read chicken-hot --limit=50
```

---

## 💰 RAPPEL DES COÛTS

- Google Cloud Run: **GRATUIT** ✅
- Firebase: **GRATUIT** ✅
- OpenAI GPT-4o: **~4,50€/mois** ✅

**Total: 4,50€/mois pour 1500 appels**

---

Bon courage ! 🚀
