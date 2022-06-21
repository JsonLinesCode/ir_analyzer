import os
from attr import assoc
from colorama import colorama_text
import matplotlib.pyplot as plt
import matplotlib.colors as color
import numpy as np
import json
from PIL import Image, ImageDraw

# Ce programme a été conçu pour recenser rapidement les couleurs d'une liste de fichiers images à la racine du programme
# Pour l'executer il faut donc le lancer là où les fichiers sont situés
# Une liste de fichiers exemptés peut être fournie et modifiée dans la variable `file_ignore` ils ne seront pas traités par le programme
# Les images doivent avoir les mêmes dimensions


# Enjoy !


# Fichiers ignorés
file_ignore = ["info.jpg", "shade.png"]

# Extension des images traitées
extension = "png"

# Le délimitateur du fichier de sortie, mieux vaut ne pas toucher  : c'est par défaut une virgule
csv_delimiter = ","


# Nom du fichier de sortie
output = "meta.csv"
# Liste d'entiers des positions des lignes de la grille (voir info.jpg) de découpage en PIXELS
# De gauche à droite et de haut en bas
# On aura toujours les lignes qui délimitent l'image (littéralement par flemme)
horizontal_grid = [0, 62, 154, 240]
vertical_grid = [0, 79, 170, 240]

# Largeur en pixels
image_width = 240
# Hauteur en pixel
image_height = 240


# Le nom du fichier contenant le spectre IR
shade_file = "shade.png"

# Nom du fichier contenant les metadonnées
meta_file = "images_meta.json"

# Liste des images du dossier


def filesList():
    file_list = []
    for folder, dirs, files in os.walk('./'):
        for file in files:

            if file.endswith(extension) and not file.startswith("grid"):
                if file not in file_ignore:
                    file_list.append(file)
    return file_list


def fileColorsScheme(fileName):
    image = plt.imread(fileName)
    dico = {}

    # On débute l'analyse
    # On regarde déjà les coordonnées des grilles
    for y_line in range(len(vertical_grid)-1):
        for x_line in range(len(horizontal_grid)-1):
            # Les identifiants de la cell (voir info.jpg)
            # J'ajoute juste 1 pour que ce soit plus facile à comprendre pour un humain, genre case (1,1) au lieu de (0,0)
            cell_x = x_line+1
            cell_y = y_line+1

            # Coordonnées des lignes de la grille en cours d'étude
            current_vline = vertical_grid[y_line]
            current_hline = horizontal_grid[x_line]
            next_vline = vertical_grid[y_line+1]
            next_hline = horizontal_grid[x_line+1]

            # On extrait la case étudiée
            extracted = image[current_vline:next_vline,
                              current_hline:next_hline]

            # Nom de la clé du dico correspondant à une cellule
            cell_name = "("+str(cell_y)+";"+str(cell_x) + ")"
            dico[cell_name] = []

            # On parcourt chaque pixel de la case étudiée
            for i in range(next_vline - current_vline):
                for j in range(next_hline - current_hline):
                    # On extrait la couleur du pixel etudié
                    color = str([str(a) for a in np.nditer(extracted[i][j])])

                    # Drapeau qui permet de passer l'étape suivante si on a déjà ajouté la couleur dans la liste
                    added = False
                    for val in dico[cell_name]:
                        if val["color"] == color:
                            val["count"] += 1
                            added = True

                    # On ajoute si la couleur n'a pas été ajoutée
                    if(not added):
                        dico[cell_name].append({
                            "color": color,
                            "count": 1
                        })
            # On triche un peu en utilisant le tri de Python intégré pour trier en fonction du nombre de pixel de telle couleur
            dico[cell_name].sort(key=sortFunction)
            dico[cell_name].reverse()
    return dico


# Petite triche pour trier par nombre d'occurences de chaque couleur
def sortFunction(e):
    return e['count']


# Calculer la température pour une couleur donnée
def calculateTemp(color, leftBound, rightBound):
    r, g, b, d = color
    image = plt.imread(shade_file)
    height, width, dimension = image.shape
    # On parcourt le spectre à la recherche de la couleur correspondante
    l = []
    for i in range(height):
        for j in range(width):
            cr, cg, cb, cd = image[i][j]
            # Le trick : on va choisir la couleur la plus proche en calculant la norme entre les deux couleurs
            diff = ((r - cr)**2 + (g - cg)**2 + (b - cb)**2) ** 1/2
            l.append((diff, j))
    # On estime la température
    return leftBound+(rightBound-leftBound) * (min(l)[1] / width)

# Obtenir l'ensemble des meta données des images du dossier (température du spectre)


def imagesMeta():
    file = open(meta_file)
    raw = file.read()
    return json.loads(raw)

# Pour écrire le fichier CSV de sortie


def fileWrite(image_name, cell_name, cell_average_temp, cell_dominant_temp):
    file = open(output, "a")
    lines = []
    lines.append(image_name+csv_delimiter+cell_name +
                 csv_delimiter + cell_average_temp + csv_delimiter + cell_dominant_temp + "\n")
    file.writelines(lines)
    file.close()

# On génère des images contenant les températures des images


def gridWrite(fileName, imageTemps):
    outputName = "./grid_outputs/grid_" + fileName
    height = image_height
    width = image_width
    img = Image.open(fileName, "r")
    # On dessine le quadrillage
    draw = ImageDraw.Draw(img)
    i = 0
    for x in horizontal_grid:
        line = ((x, 0), (x, height))
        draw.line(line, fill=128)
    for y in vertical_grid:
        line = ((0, y), (height, y))
        draw.line(line, fill=128)
    # On écrit les textes
    for x in range(0, image_width, image_width // 3):

        draw.text((width * 0.03, x + 15), imageTemps[i][0] + "\n" +
                  imageTemps[i][1], fill="white")
        draw.text((width * 0.3, x + 15), imageTemps[i+1][0] + "\n" +
                  imageTemps[i+1][1], fill="white")

        draw.text((width * 0.7, x + 15), imageTemps[i+2][0] + "\n" +
                  imageTemps[i+2][1], fill="white")

        i += 3
    # On sauvegarde
    img.save(outputName)


# Pour effacer le fichier de sortie et rajouter la première ligne de description

def clearOutput():
    f = open(output, 'w')
    f.write("nom_fichier"+csv_delimiter +
            "nom_cellule"+csv_delimiter+"temperature_moyenne" + csv_delimiter + "temperature_dominante\n")
    f.close()


# On cherche les images dans le dossier
files = filesList()

# On importe leurs méta données (les températures max et min renseignées dans un fichier JSON)
meta = imagesMeta()

# On efface le fichier CSV d'origine
clearOutput()

# C'est parti pour le grand traitement !
for file in files:
    print("Traitement de " + file + " ...")
    dico = fileColorsScheme(file)
    cellTemps = []
    for cellname in dico.keys():
        # La couleur la plus présente dans la partie de l'image
        dominantColor = [
            float(a) for a in eval(dico[cellname][0]["color"])]
        # La couleur moyenne des couleurs code dégueu mais qui marche
        colorList = dico[cellname]
        averageColor = []
        for i in colorList:
            for j in range(i["count"]):
                averageColor.append([
            float(a) for a in eval(i["color"])])
        averageColor = np.average(averageColor, axis=0)

        # La température pour la couleur la plus présente dans la cellule
        tempDominant = calculateTemp(
            dominantColor, meta[file]["left_bound"], meta[file]["right_bound"])

        # La température pour la couleur moyenne dans la cellule
        tempAverage = calculateTemp(
            averageColor, meta[file]["left_bound"], meta[file]["right_bound"])
        # On a enfin fini ! On imprime dans le fichier CSV
        fileWrite(file, cellname,  str(tempAverage), str(tempDominant))
        cellTemps.append(["M {:0.2f}ºC.\n".format(tempAverage),
                         "D {:0.2f}ºC.\n".format(tempDominant)])
    # Petite folie, on exporte une image qui contient une grille avec les températures de chaque objet
    gridWrite(file, cellTemps)
