# Utilise une image Python légère
FROM python:3.11-slim

# Définit le répertoire de travail à l'intérieur du conteneur
WORKDIR /app

# Copie le fichier de dépendances
COPY requirements.txt .

# Installe les dépendances nécessaires, y compris setuptools et pip
RUN pip install --no-cache-dir --upgrade pip setuptools

# Installe les dépendances de votre application
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code de l'application dans le conteneur
COPY . .

# Expose le port 8000 pour accéder à l'application
EXPOSE 8000

# Commande pour lancer l'application avec Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
