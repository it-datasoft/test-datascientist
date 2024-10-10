# Test Technique Data Scientist - GED

Durée : 5h

## Contexte :
Vous recevez un ensemble de documents administratifs typiques pour une collectivité (actes de naissance, passeports, certificats, …). Votre tâche consiste à :
1.	Extraire des données structurées à partir de ces documents.
2.	Annoter les entités nommées sous la forme de paires clé-valeur dans un format JSON.

## Livrables attendus :
Un script ou une API capable de prendre en entrée un fichier et de renvoyer les données extraites et annotées sous forme de JSON.


## Plan d'exécution

Pour réaliser un script ou une API capable de prendre en entrée un fichier et de renvoyer les données extraites et annotées sous forme de JSON, il faudra d'abord avoir des documents en entrée. Les documents fournis ici sont des actes de naissance, des passeports, des certificats ou encore actes de mariage et une carte nationale d'identité(CNI) qui serint rassemblés dans un dossier "inputs".

Le but est d'avoir comme sortie, quelque soit le document, des données annotées.

Dans un premier temps on définira toutes les variables statiques qu'on mettra dans un fichier .env . On prendra aussi le soin de mettre en place un environnement virtuel dans lequel on effectuera tous les imports et les installations (dans le but d'isoler les paquets utilisés pour le projet, afin de pouvoir éviter les conflits de versions avec les paquets préalablement installés). 

Ensuite, nous passerons à l'installation et l'import de toutes les librairies concernant le projet GED. On s'assurera de n'avoir que des librairies utilisées afin de ne pas surcharger l'environnement virtuel.

Par la suite, nous allons nous ateler à l'extraction. Nous allons mettre en place, premièrement, toutes les fonctions précédant l'extraction : la fonction qui permettra de savoir le type du document implémenté, le pré-traitement de l'image pour que l'image soit plus lisible lors de l'extraction du texte, la fonction d'extraction de la photo pour pouvoir l'appeler dans la fonction d'extraction et obtenir l'extraction et la photo (sera utilisée aussi pour la signature et le cachet que contient l'image), la fonction qui va nettoyer le texte extrait pour enlever tout les retours chariots, les espaces de trop et les caractères constituant les bruits de l'extraction, une ia qui permettra d'affiner le texte extrait pour une meilleure labellisation et enfin l'extraction.


Après, nous aurons l'étape de formattage des données dans le but de mettre les données dectectées qui n'ont pas la bonne forme (telles que les dates par exemple) dans la forme requise dans le fichier json.

Enfin, nous ferons la labellisation en fonction du type de document avec la définition des champs voulus, puis, l'implémentation d'une ia capable de reconnaitre les données pour les classer dans des labels, remplissage de ces labels et enfin le renvoie de ces labels remplis par un fichier json.

Pour résumer

1. Settup 

a. Le fichier .env
b. Le fichier venv
c. Installations
d. Imports

2. Extraction

a. Fonction de détection du type de document
b. Pré-traitement de l'image
c. Fonction d'extraction de la photo
d. Fonction de nettoyage
e. IA pour améliorer 
f. Extraction

3. Formattage

a. Les dates

4. Labellisation

a. Définition des champs
b. Reconnaissance des données
c. Labellisation
d. Renvoi