# start_app.sh
#!/bin/bash

# Démarre l'application FastAPI
uvicorn app:app --host 0.0.0.0 --port 8000 &

# Démarre ngrok pour exposer le port 8000
ngrok http 8000