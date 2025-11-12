# 📁 LISTE COMPLÈTE DES FICHIERS

Voici TOUS les fichiers que tu as téléchargés et où les placer :

---

## 📂 STRUCTURE FINALE

```
chicken-hot-system/                    ← Crée ce dossier
│
├── server.py                          ← Fichier téléchargé
├── order_analyzer.py                  ← Fichier téléchargé
├── requirements.txt                   ← Fichier téléchargé
├── Dockerfile                         ← Fichier téléchargé
├── .dockerignore                      ← Fichier téléchargé
├── .gitignore                         ← Fichier téléchargé
├── firebase-key.json                  ← À télécharger depuis Firebase
│
├── static/                            ← Crée ce sous-dossier
│   ├── index.html                     ← Renomme static_index.html
│   ├── style.css                      ← Renomme static_style.css
│   └── app.js                         ← Renomme static_app.js
│
└── README.md                          ← Fichier téléchargé (optionnel)
```

---

## ✅ CHECKLIST

### Fichiers Racine (9 fichiers)

- [ ] `server.py` - Serveur Flask principal
- [ ] `order_analyzer.py` - Analyseur IA avec OpenAI
- [ ] `requirements.txt` - Liste des dépendances Python
- [ ] `Dockerfile` - Configuration pour Docker
- [ ] `.dockerignore` - Fichiers à ignorer par Docker
- [ ] `.gitignore` - Fichiers à ignorer par Git
- [ ] `firebase-key.json` - **À télécharger depuis Firebase Console**
- [ ] `README.md` - Documentation (optionnel)
- [ ] `GUIDE_SIMPLE.md` - Guide de déploiement (optionnel)

### Fichiers dans le dossier `static/` (3 fichiers)

- [ ] `static/index.html` - Interface web (renommer `static_index.html`)
- [ ] `static/style.css` - Styles CSS (renommer `static_style.css`)
- [ ] `static/app.js` - Logique JavaScript (renommer `static_app.js`)

---

## 🔄 ACTIONS À FAIRE

### 1. Créer les dossiers

```bash
mkdir chicken-hot-system
cd chicken-hot-system
mkdir static
```

### 2. Placer les fichiers téléchargés

**Dans `chicken-hot-system/` (racine) :**
- `server.py`
- `order_analyzer.py`
- `requirements.txt`
- `Dockerfile`
- `.dockerignore`
- `.gitignore`
- `README.md`
- `GUIDE_SIMPLE.md`

**Dans `chicken-hot-system/static/` :**
- Renomme `static_index.html` en `index.html` et place ici
- Renomme `static_style.css` en `style.css` et place ici
- Renomme `static_app.js` en `app.js` et place ici

### 3. Ajouter firebase-key.json

1. Va sur Firebase Console
2. Télécharge les clés (voir GUIDE_SIMPLE.md)
3. Renomme en `firebase-key.json`
4. Place dans `chicken-hot-system/` (racine)

⚠️ **NE PAS** commiter ce fichier sur GitHub !

---

## 🎯 FICHIERS PAR FONCTION

### Backend (Python)
- `server.py` - API Flask
- `order_analyzer.py` - Analyse IA des commandes
- `requirements.txt` - Dépendances

### Frontend (Interface Restaurant)
- `static/index.html` - Structure HTML
- `static/style.css` - Design et animations
- `static/app.js` - Logique en temps réel avec Firebase

### Configuration
- `Dockerfile` - Build Docker pour Cloud Run
- `.dockerignore` - Fichiers à exclure du build
- `.gitignore` - Fichiers à ne pas versionner

### Documentation
- `README.md` - Documentation technique complète
- `GUIDE_SIMPLE.md` - Guide pas à pas pour déployer
- `LISTE_FICHIERS.md` - Ce fichier !

### Secrets (à créer)
- `firebase-key.json` - Clés d'accès Firebase

---

## 🔍 VÉRIFICATION

Une fois tout placé, ta structure doit ressembler à ça :

```
chicken-hot-system/
│
├── 📄 server.py
├── 📄 order_analyzer.py
├── 📄 requirements.txt
├── 📄 Dockerfile
├── 📄 .dockerignore
├── 📄 .gitignore
├── 🔑 firebase-key.json
├── 📖 README.md
├── 📖 GUIDE_SIMPLE.md
├── 📖 LISTE_FICHIERS.md
│
└── 📁 static/
    ├── 🌐 index.html
    ├── 🎨 style.css
    └── ⚙️ app.js
```

**Compte:**
- Dossier racine: 10 fichiers
- Dossier static: 3 fichiers
- **Total: 13 fichiers**

---

## ❓ FAQ

**Q: Je ne trouve pas un fichier**
R: Assure-toi d'avoir téléchargé TOUS les fichiers depuis Claude

**Q: static_index.html, c'est quoi ?**
R: C'est `index.html` mais préfixé pour le téléchargement. Renomme-le !

**Q: Où est firebase-key.json ?**
R: Il faut le télécharger depuis Firebase Console (voir GUIDE_SIMPLE.md)

**Q: .gitignore ne s'affiche pas**
R: Normal, les fichiers commençant par `.` sont cachés. Active "Afficher les fichiers cachés"

**Q: Je peux supprimer les .md ?**
R: Oui, README.md et GUIDE_SIMPLE.md sont optionnels

---

## 🚀 PRÊT ?

Si tu as bien tous les fichiers au bon endroit, tu peux passer au déploiement !

👉 Suis le **GUIDE_SIMPLE.md** pour déployer étape par étape

Bon courage ! 🎉
