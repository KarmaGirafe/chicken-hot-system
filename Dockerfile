# Image Python légère
FROM python:3.11-slim

# Répertoire de travail
WORKDIR /app

# Copie les dépendances
COPY requirements.txt .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code
COPY . .

# Port par défaut Cloud Run
ENV PORT=8080

# Commande de démarrage
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 server:app
