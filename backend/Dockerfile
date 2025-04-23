# Étape 1 : choisir l'image de base (Python 3.10 slim pour être léger)
FROM python:3.10-slim

# Étape 2 : définir le répertoire de travail
WORKDIR /app

# Étape 3 : copier le fichier des dépendances et installer les packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Étape 4 : copier le code source dans l’image Docker
COPY app/ .

# Étape 5 : lancer l'application avec uvicorn (FastAPI server)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
