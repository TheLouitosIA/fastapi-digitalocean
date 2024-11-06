import psycopg2
import os
import cv2  # Import OpenCV pour lire l'image
from fastapi import FastAPI, File, UploadFile
import detect  # Importation du script YOLO
from db_connection import get_connection
import json  # Import JSON pour convertir le dictionnaire
from datetime import datetime, timedelta
from fastapi import Query
from typing import Optional
from fastapi import Depends, HTTPException, Header
from pydantic import EmailStr, constr
from datetime import date
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, constr, field_validator
import re

app = FastAPI()
date_prise = datetime.now().isoformat()  # Format ISO pour la date et heure actuelle
API_TOKEN = "AXL_api_key_validation314"

# Modèle Pydantic pour les utilisateurs
class User(BaseModel):
    nom: constr(min_length=2, max_length=50) # type: ignore
    prenom: constr(min_length=2, max_length=50) # type: ignore
    email: EmailStr
    telephone: str
    marque_voiture: constr(min_length=2, max_length=50) # type: ignore
    plaque_immatriculation: constr(min_length=2, max_length=15) # type: ignore

    @field_validator('telephone')
    def telephone_format(cls, v):
        if not re.match(r'^\+?1?\d{9,15}$', v):
            raise ValueError("Le numéro de téléphone n'est pas dans un format valide.")
        return v

class Photo(BaseModel):
    utilisateur_id: int
    type_photo: str
    chemin_photo: str
    date_prise: str  # Format ISO 8601, ex : "2024-11-01T12:00:00"

class Validation(BaseModel):
    utilisateur_id: int
    mois_verification: str  # Format YYYY-MM, par exemple "2024-11"
    resultat: bool

class RecherchePhoto(BaseModel):
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None

# Connexion à la base de données
def get_connection():
    return psycopg2.connect(
        dbname="chauffeurs_db",
        user="app_user",
        password="AXL_userapp",
        host="localhost",
        port="5432"
    )

def verify_token(x_api_token: str = Header(...)):
    if x_api_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Accès non autorisé")

@app.post("/detect/")
async def detect_vehicle(utilisateur_id: int, type_photo: str, image: UploadFile = File(...)):
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    image_path = os.path.join(temp_dir, image.filename)
    try:
        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())

        image_np = cv2.imread(image_path)
        results = detect.detect_image(image_np)
        is_valid = detect.validate_detection(type_photo, results)
        validation_status = "validé" if is_valid else "non validé"

        results_formatted = [
            {
                "bbox": result["bbox"],
                "confidence": round(result["confidence"], 2),
                "class_id": result["class"]
            }
            for result in results
        ]
        
        results_json = json.dumps(results_formatted)
        conn = get_connection()
        cur = conn.cursor()

        # Insertion de la photo avec son statut de validation
        date_prise = datetime.now().isoformat()
        mois_verification = datetime.now().strftime("%Y-%m")
        query = """
            INSERT INTO photos (utilisateur_id, type_photo, chemin_photo, date_prise, resultat_detection, statut_validation)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (
            utilisateur_id,
            type_photo,
            image_path,
            date_prise,
            results_json,
            validation_status
        ))

        # Vérification si toutes les photos requises pour le mois sont validées
        cur.execute("""
            SELECT COUNT(*)
            FROM photos
            WHERE utilisateur_id = %s 
            AND date_trunc('month', date_prise) = date_trunc('month', %s::timestamp) 
            AND statut_validation = 'validé'
        """, (utilisateur_id, mois_verification + "-01"))

        photos_valides = cur.fetchone()[0]
        if photos_valides >= 4:  # Par exemple, 4 sur 5 photos doivent être validées (sauf "compteur")
            # Insère ou met à jour la validation mensuelle si toutes les photos sont validées
            cur.execute("""
                INSERT INTO validations (utilisateur_id, mois_verification, resultat)
                VALUES (%s, %s, TRUE)
                ON CONFLICT (utilisateur_id, mois_verification)
                DO UPDATE SET resultat = TRUE
            """, (utilisateur_id, mois_verification))

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return {"error": f"Erreur lors de l'ajout de la photo : {e}"}
    finally:
        os.remove(image_path)

    return {
        "detections": results_formatted,
        "validation_status": validation_status
    }
