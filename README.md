# Test Technique Data Scientist - GED

Durée : 5h

## Contexte :
Vous recevez un ensemble de documents administratifs typiques pour une collectivité (actes de naissance, passeports, certificats, …). Votre tâche consiste à :
1.	Extraire des données structurées à partir de ces documents.
2.	Annoter les entités nommées sous la forme de paires clé-valeur dans un format JSON.

## Livrables attendus :
Un script ou une API capable de prendre en entrée un fichier et de renvoyer les données extraites et annotées sous forme de JSON.


<!-- #Etape pour réaliser le test -->

Faire le nettoyage  des données si nécessaire
l'écriture des données en utf8(reour charriot, espace inutile, symbole)


<!-- Étape 1 : Nettoyage des données -->
    <!-- Nettoyage du texte : -->
Encodage du texte en UTF-8.
Suppression des caractères spéciaux, retours chariot inutiles, espaces superflus.
Normalisation du texte.

    <!-- Nettoyage des images : -->
Prétraitement des images (ajustement du contraste, redimensionnement, amélioration de la clarté).
Utilisation de bibliothèques comme Pillow ou OpenCV pour traiter les images.


<!-- Étape 2 : Extraction des données -->
Extraction du texte :
Utilisation d'un outil OCR comme Tesseract pour extraire le texte à partir des images(installation).
Extraction des images spécifiques :
Extraction des photos, signatures et cachets présents dans les documents.
Conversion de l'image en texte.
Encodage des images en base64.

Étape 3 : Annotation des entités nommées
Traitement NLP (Reconnaissance des entités nommées - NER) :
Utilisation d'un modèle NLP (comme spaCy ou Transformers) pour annoter les entités (nom, prénom, date de naissance, lieu, etc.).
Stockage des annotations sous forme de paires clé-valeur :
Formatage des annotations dans un fichier JSON.

Étape 4 : Encodage des images
Encodage des images en base64 :
Photos, signatures et cachets extraits sont encodés en base64 pour être intégrés dans la sortie JSON.

Étape 5 : Développement d'un script ou d'une API
Développement d'un script :
Créer une script capable de recevoir un fichier (document image) en entrée.
Extraire les données, effectuer les annotations, et renvoyer un fichier JSON structuré avec les images encodées en base64.