import os
import matplotlib.pyplot as plt
import matplotlib.colors as color
import numpy

# Ce programme a été conçu pour recenser rapidement les couleurs d'une liste de fichiers images à la racine du programme
# Pour l'executer il faut donc le lancer là où les fichiers sont situés
# Une liste de fichiers exemptés peut être fournie et modifiée dans la variable `file_ignore` ils ne seront pas traités par le programme
# Les images doivent avoir les mêmes dimensions


# Enjoy ! 

# Décommenter au cas où on veut changer de dossier (bof)
# os.chdir("(nouvelle position)")

# Fichiers ignorés
file_ignore = ["info.jpg"]

# Extension des images traitées
extension = "jpg"

# Le délimitateur du fichier de sortie, mieux vaut ne pas toucher  : c'est par défaut une virgule
csv_delimiter = ","


# Nom du fichier de sortie
output = "meta.csv"
# Liste d'entiers des positions des lignes de la grille (voir info.jpg) de découpage en PIXELS
# De gauche à droite et de haut en bas
# On aura toujours les lignes qui délimitent l'image (littéralement par flemme)
horizontal_grid = [0, 62, 154, 240]
vertical_grid = [0, 79, 170, 240 ]

# Largeur en pixels
image_width = 240
# Hauteur en pixel
image_height = 240
# Liste de fichiers à traiter
def filesList():
    file_list = []
    for folder, dirs, files in os.walk('./'):
        for file in files:
            if file.endswith(extension):
                if file not in file_ignore:
                    file_list.append(file)
    return file_list 


def fileColorsScheme(fileName):
    image = plt.imread(fileName)
    dico =  {}
    
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
            extracted = image[current_vline:next_vline,current_hline:next_hline]
            cell_name = "("+str(cell_x)+";"+str(cell_y) + ")"
            avg_color_per_row = numpy.average(extracted, axis=0)
            avg_color = numpy.average(avg_color_per_row, axis=0)
            dico[cell_name] = color.to_hex([x / 255.0 for x in avg_color])
            """ # On parcourt chaque pixel de la case étudiée
            for i in range(next_vline- current_vline):
                for j in range(next_hline- current_hline):

                    # Nom de la clé du dico correspondant à une cellule 
                    cell_name = "("+str(cell_x)+";"+str(cell_y) + ")"
                    if cell_name not in dico:
                        dico[cell_name] = {}
                    color_name =   str(extracted[i][j])
                    # On extrait la couleur du pixel etudié
                    
                    if color_name not in dico[cell_name]:
                        dico[cell_name][color_name] = 1
                    else:
                        dico[cell_name][color_name] += 1 """

    return dico

# Pour écrire le fichier de sortie
def fileWrite( image_name, cell_average_color, cell_name):

    file = open(output, "a")
    lines = []
    
    lines.append(image_name+csv_delimiter+cell_name+csv_delimiter+cell_average_color +"\n")
    file.writelines(lines)
    file.close()

# Pour effacer le fichier de sortie et rajouter la première ligne de description
def clearOutput():
    f = open(output, 'w')
    f.write("nom_fichier"+csv_delimiter+"nom_cellule"+csv_delimiter+"couleur\n")
    f.close()

files = filesList()

clearOutput()
for file in files:
    print("Traitement de " + file + " ...")
    dico = fileColorsScheme(file)

    for cellname in dico.keys():
        fileWrite(file,  dico[cellname], cellname)
        



