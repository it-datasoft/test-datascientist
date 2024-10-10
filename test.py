import pytesseract
from PIL import Image
from transformers import pipeline
import cv2
import numpy as np
import os
import re
import json
import spacy
import base64



PREPROCESSED_FOLDER= os.environ.get("pre_prossed_path")

"""
Extraction des photos
"""""


def extract_faces_from_passport(image_path, output_folder='./outputs'):
    # Charger le classificateur en cascade pour la détection de visages
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Lire l'image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Détecter les visages
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # Créer un dossier pour stocker les visages extraits
    os.makedirs(output_folder, exist_ok=True)

    face_count = 0
    for (x, y, w, h) in faces:
        # Extraire le visage de l'image
        face = image[y:y + h, x:x + w]

        # Enregistrer le visage extrait
        face_filename = os.path.join(output_folder, f'face_{face_count}.jpg')
        cv2.imwrite(face_filename, face)
        face_count += 1

    with open(face_filename, 'rb') as image_file:
        # Lire l'image en mode binaire
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    return encoded_string

    

# Exemple d'utilisation :
# extracted_photo = extract_passport_photo("chemin_vers_image_du_passeport.jpg")
# if extracted_photo:
#     print(f"Photo extraite et sauvegardée à : {extracted_photo}")
# else:
#     print("Impossible de trouver la photo dans l'image du passeport.")

""""
Pré-traitement de l'image
"""""

# 

# Exemple d'utilisation
# preprocessed_img = preprocess_image('chemin_vers_image.jpg')



# # Sauvegarder ou afficher l'image prétraitée pour vérifier le résultat
# cv2.imshow('Prétraitement', preprocessed_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# # Sauvegarder l'image prétraitée
# cv2.imwrite('preprocessed_image.jpg', preprocessed_img)


def classify_document(text):
    """
    Classifie un document administratif en fonction du texte extrait.
    :param text: Texte extrait du document (chaîne de caractères)
    :return: Type de document (str)
    """
    # Convertir le texte en minuscules pour éviter les erreurs dues à la casse
    text = text.lower()

    # Mots-clés pour chaque type de document
    keywords = {
        "passeport": [
            "passeport", "passport", "numéro de passeport", "date d'expiration", "nationalité", "date de délivrance"
        ],
        "cni": [
            "carte nationale d'identité", "cni", "numéro d'identité", "date de naissance", "lieu de naissance",
            "date de délivrance", "autorité de délivrance", "nationalité"
        ],
        "acte de naissance": [
            "acte de naissance", "nom de l'enfant", "date de naissance", "lieu de naissance", "nom du père", "nom de la mère"
        ],
        "certificat de mariage": [
            "certificat de mariage", "acte de mariage", "nom du marié", "nom de la mariée", "date du mariage",
            "lieu du mariage", "témoins", "officier d'état civil"
        ]
    }

    # Boucle sur les mots-clés pour classifier le document
    for doc_type, doc_keywords in keywords.items():
        if any(keyword in text for keyword in doc_keywords):
            return doc_type

    # Si aucun type ne correspond
    return "Type de document inconnu"

def clean_text(text):
    
    text = re.sub(r'[^a-zA-Z0-9éèêëîïôûûÀÂÄÇÉÈÊËÎÏÔÛ\s]', '', text)
    
    # Remplacer les multiples espaces par un espace unique
    text = re.sub(r'\s+', ' ', text)
    
    # Supprimer les espaces en début et fin de chaîne
    text = text.strip()
    
    return text


def extract_text(image_path):
    img = Image.open(image_path)
    photo=extract_faces_from_passport(image_path)
    text = pytesseract.image_to_string(img)
    clean_texte=clean_text(text)
    return clean_texte

def correct_text_with_gpt(text):
    gpt_pipeline = pipeline('text-generation', model='gpt2')
    corrected_text = gpt_pipeline(text, max_length=len(text) + 50, do_sample=False)[0]['generated_text']
    return corrected_text

# Pipeline complet : OCR + Correction IA
def ocr_with_ai(image_path):
    # Étape 1 : Extraction du texte
    extracted_text = extract_text(image_path)
    print(f"Texte extrait : {extracted_text}")
    
    # Étape 2 : Correction avec GPT
    corrected_text = correct_text_with_gpt(extracted_text)
    _type = classify_document(corrected_text)
    print(f"Texte corrigé : {corrected_text}")
    
    return corrected_text

# Exemple d'utilisation



"""
Formattage
"""""
import re

def text_to_number(text):
    """
    Transforme un texte numérique (en lettres) en un nombre entier.
    :param text: Texte à transformer (str)
    :return: Nombre entier (int)
    """
    # Dictionnaires pour les unités et les dizaines
    units = {
        'zéro': 0, 'un': 1, 'deux': 2, 'trois': 3, 'quatre': 4,
        'cinq': 5, 'six': 6, 'sept': 7, 'huit': 8, 'neuf': 9
    }

    teens = {
        'dix': 10, 'onze': 11, 'douze': 12, 'treize': 13, 'quatorze': 14,
        'quinze': 15, 'seize': 16
    }

    tens = {
        'vingt': 20, 'trente': 30, 'quarante': 40, 'cinquante': 50, 'soixante': 60,
        'soixante-dix': 70, 'quatre-vingt': 80, 'quatre-vingt-dix': 90
    }

    # Dictionnaire pour les milliers
    thousands = {
        'mille': 1000
    }

    # Remplacer les mots par des nombres
    words = text.split()
    total = 0
    current_number = 0

    for word in words:
        if word in units:
            current_number += units[word]
        elif word in teens:
            current_number += teens[word]
        elif word in tens:
            current_number += tens[word]
        elif word in thousands:
            current_number *= thousands[word]
            total += current_number
            current_number = 0
        elif word == 'et':
            continue  # Ignore 'et'

    total += current_number
    return total

def transform_date(text_date):
    """
    Transforme une date écrite dans un format littéral en format numérique (YYYY-MM-DD).
    :param text_date: Date sous forme de texte (str)
    :return: Date en format numérique (str) ou None si la date est invalide
    """
    # Expression régulière pour extraire l'année, le jour et le mois
    match = re.search(r"l'an (.+), le (.+) jour du mois de (.+)", text_date)

    if match:
        year_text = match.group(1).strip()
        day_text = match.group(2).strip()
        month_text = match.group(3).strip()

        # Convertir l'année, le jour et le mois en nombres
        year = text_to_number(year_text)
        day = text_to_number(day_text)
        
        # Dictionnaire pour les mois
        months = {
            'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
            'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
            'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
        }

        month = months.get(month_text)

        if month:
            # Formater la date en YYYY-MM-DD
            formatted_date = f"{year}-{month}-{day:02}"
            return formatted_date

    return None  # Si la date n'est pas valide

# Exemple d'utilisation
text_date = "l'an deux mille vingt, le cinquième jour du mois de novembre"
formatted_date = transform_date(text_date)
print(f"Date formatée : {formatted_date}")

"""
Labellisation e-form
"""""

# Charge le modèle de langue français de spaCy
nlp = spacy.load("fr_core_news_sm")

photo = extract_faces_from_passport("./outputs/mariage1.jpg")

# Fonction pour extraire les informations du texte
def extract_info(text):

    data = {
        "certificat_de_mariage": {
            "type_document": "certificat de mariage",
            "date_mariage": "",
            "lieu": {
                "continent": "",
                "pays": "",
                "ville": "",
                "quartier": ""
            },
            "epoux": [
                {
                    "nom": "",
                    "prenom": "",
                    "date_naissance": "",
                    "nationalite": "",
                    "parents": {
                        "pere": {
                            "nom": "",
                            "prenom": "",
                            "nationalite": ""
                        },
                        "mere": {
                            "nom": "",
                            "prenom": "",
                            "nationalite": ""
                        }
                    }
                },
                {
                    "nom": "",
                    "prenom": "",
                    "date_naissance": "",
                    "nationalite": "",
                    "parents": {
                        "pere": {
                            "nom": "",
                            "prenom": "",
                            "nationalite": ""
                        },
                        "mere": {
                            "nom": "",
                            "prenom": "",
                            "nationalite": ""
                        }
                    }
                }
            ],
            "officier_etat_civil": {
                "nom": "",
                "prenom": "",
                "titre": ""
            },
            "remarques": "",
            "photo":""
        }
    }

    # Extraction des informations
    # Utiliser des regex ou spaCy pour trouver les informations
    # Exemple simple pour extraire le nom des époux et la date de mariage

    # Regex pour la date
    date_match = re.search(r"date(?: du)? mariage :? (\d{1,2} \w+ \d{4})", text)
    if date_match:
        data["certificat_de_mariage"]["date_mariage"] = date_match.group(1)

    # Exemple d'extraction de noms d'époux
    epoux_matches = re.findall(r"époux? :? ([\w\s]+) et ([\w\s]+)", text)
    if epoux_matches:
        for i, nom_prenom in enumerate(epoux_matches[0]):
            # Diviser le nom et prénom
            nom_prenom_split = nom_prenom.split()
            if len(nom_prenom_split) >= 2:
                data["certificat_de_mariage"]["epoux"][i]["nom"] = nom_prenom_split[-1]
                data["certificat_de_mariage"]["epoux"][i]["prenom"] = " ".join(nom_prenom_split[:-1])

    # Exemple d'extraction du lieu
    lieu_match = re.search(r"lieu :? ([\w\s]+)", text)
    if lieu_match:
        data["certificat_de_mariage"]["lieu"]["ville"] = lieu_match.group(1)

    photo = photo

    # Ajouter d'autres extractions pour les parents, l'officier d'état civil, etc.

    return data

final_text = ocr_with_ai('./inputs/mariage1.jpg')
data=extract_info(final_text)
print(data)

# # Fonction principale
# def main(image_path):
#     # Étape 1 : Effectuer l'OCR
#     extracted_text = ocr_from_image(image_path)

#     # Étape 2 : Extraire les informations et remplir le JSON
#     filled_data = extract_info(extracted_text)

#     # Convertir en JSON
#     json_output = json.dumps(filled_data, indent=4, ensure_ascii=False)
#     print(json_output)
