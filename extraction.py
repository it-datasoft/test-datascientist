import easyocr
import spacy
import json
import re
import base64
import os
import cv2
import numpy as np

# Initialisation du modèle NLP
nlp = spacy.load('fr_core_news_md')

# Initialisation de EasyOCR
reader = easyocr.Reader(['fr'])

# Fonction pour extraire le texte d'une image via OCR
def extraire_texte(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Le fichier {image_path} n'existe pas.")
    
    print("Conversion de l'image en texte...")
    # Chargement de l'image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Amélioration de la qualité de l'image pour OCR
    _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Utilisation d'EasyOCR pour extraire le texte
    result = reader.readtext(binary_image, detail=0, paragraph=True)
    texte = " ".join(result)

    # Nettoyage du texte extrait
    clean_text_1 = re.sub(r'\s+', ' ', texte)  # Suppression des espaces superflus
    clean_text = re.sub(r'[^\w\s\.,:\-\+\(\)\[\]\{\}\?\!\;\"]', '', clean_text_1)  # Suppression des caractères spéciaux
    return clean_text.strip()

# Fonction pour formater la date
def formater_date(date_str):
    match = re.search(r"(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})", date_str)
    if match:
        mois_dict = {
            "janvier": "01", "février": "02", "mars": "03", "avril": "04",
            "mai": "05", "juin": "06", "juillet": "07", "août": "08",
            "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12"
        }
        return f"{match.group(1).zfill(2)}/{mois_dict.get(match.group(2).lower())}/{match.group(3)}"
    return date_str  # Retourne la chaîne originale si aucune correspondance

# Fonction pour convertir une image en base64
def convertir_image_en_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

# Fonction pour détecter et extraire les images d'un document
def extraire_images(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Détecter les contours
    contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    images_base64 = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # Ajustez cette valeur selon vos besoins
            x, y, w, h = cv2.boundingRect(contour)
            roi = image[y:y+h, x:x+w]
            images_base64.append(convertir_image_en_base64(roi))
    
    return images_base64

# Étape 2 : Extraction des données
# Fonction pour structurer les données extraites pour un formulaire de mariage
def structurer_donnees(texte):
    eform = {
        "adresseMariage": {
            "continent": "",
            "pays": "",
            "quartier": "",
            "ville": ""
        },
        "dateMariage": "",
        "documentType": "certificatMariage",
        "informationEpouse": {
            "dateNaissance": "",
            "lieuNaissance": "",
            "nom": "",
            "parents": {
                "mere": "",
                "pere": ""
            },
            "prenom": "",
            "profession": "",
            "temoins": []
        },
        "informationEpoux": {
            "dateNaissance": "",
            "lieuNaissance": "",
            "nom": ""
        }
    }

    # Étape 3 : Annotation des entités nommées
    # Analyse du texte avec spaCy pour détecter les entités nommées
    doc = nlp(texte)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            if "épouse" in ent.text.lower():
                eform["informationEpouse"]["nom"] = ent.text
            else:
                eform["informationEpoux"]["nom"] = ent.text
        elif ent.label_ == "DATE":
            eform["dateMariage"] = formater_date(ent.text)
        elif ent.label_ == "GPE":
            if eform["adresseMariage"]["pays"] == "":
                eform["adresseMariage"]["pays"] = ent.text
            else:
                eform["adresseMariage"]["ville"] = ent.text

    # Processus d'extraction personnalisé
    lines = texte.splitlines()
    for line in lines:
        line = line.strip()

        # Extraction de la date de mariage
        if "marié" in line.lower():
            date_match = re.search(r"(marié le|le|Date de mariage)\s*(\w+\s+\d+\s+\w+\s+\d+)", line)
            if date_match:
                eform["dateMariage"] = formater_date(date_match.group(2).strip())

        # Extraction des noms et autres informations
        if "Nom:" in line:
            parts = line.split("Nom:")
            if len(parts) > 1:
                eform["informationEpouse"]["nom"] = parts[1].strip()

        if "Prénom:" in line:
            parts = line.split("Prénom:")
            if len(parts) > 1:
                eform["informationEpouse"]["prenom"] = parts[1].strip()

        if "profession" in line.lower():
            parts = line.split("profession:")
            if len(parts) > 1:
                eform["informationEpouse"]["profession"] = parts[1].strip()

        if "lieu de naissance" in line.lower():
            parts = line.split("lieu de naissance:")
            if len(parts) > 1:
                eform["informationEpouse"]["lieuNaissance"] = parts[1].strip()

        # Extraction des informations sur l'époux
        if "Nom de l'époux" in line:
            parts = line.split("Nom de l'époux:")
            if len(parts) > 1:
                eform["informationEpoux"]["nom"] = parts[1].strip()

        if "Date de naissance époux" in line:
            parts = line.split("Date de naissance époux:")
            if len(parts) > 1:
                eform["informationEpoux"]["dateNaissance"] = parts[1].strip()

        if "lieu de naissance époux" in line:
            parts = line.split("lieu de naissance époux:")
            if len(parts) > 1:
                eform["informationEpoux"]["lieuNaissance"] = parts[1].strip()

    return eform

# Fonction principale pour traiter l'image et générer le JSON
def traiter_document(image_path, output_file):
    texte_extrait = extraire_texte(image_path)
    if not texte_extrait:
        print("Aucun texte extrait. Veuillez vérifier l'image.")
        return

    donnees_structurees = structurer_donnees(texte_extrait)

    # Convertir uniquement les images détectées dans le document
    images_base64 = extraire_images(image_path)

    # Créer un dictionnaire combiné avec les résultats
    resultat_final = {
        "extractionTexte": texte_extrait,
        "images_base64": images_base64 if images_base64 else None,
        "eform": donnees_structurees
    }

    # Étape 4 : Enregistrement dans un fichier JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultat_final, f, ensure_ascii=False, indent=4)

# Exemple d'utilisation
image_path = 'C:/testgemima/inputs/mariage1.jpg'
output_file = 'C:/testgemima/outputs/resultat.json'
traiter_document(image_path, output_file)
