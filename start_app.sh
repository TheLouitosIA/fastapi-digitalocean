#!/bin/bash

# Activer l'environnement virtuel
source venv/bin/activate

# Démarrer l'application FastAPI
uvicorn app:app --host 0.0.0.0 --port 80 &

# Lancer ngrok avec le sous-domaine statique configuré dans ngrok.yml
ngrok start default
