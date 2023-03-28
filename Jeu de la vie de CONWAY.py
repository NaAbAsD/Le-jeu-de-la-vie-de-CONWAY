from tkinter import * # Import inferface globale
import tkinter.filedialog as loader # Import gestionnaire de fichiers
import tkinter.messagebox as box # Import warnings
import tkinter.font as font # Import police écriture
import ctypes # Import taille ecran
import time # Import calcul temps
import random # Import aléatoire

# Police d'écriture variables
fontSizeTitle = 12
fontName = "Arial"
fontSizeDesc = 10


### Variables initialisées pour modification futures ###
jours = 0
nbCells = 0
sec = 0
tailleDeLaGrille = 0
widthGrille = ctypes.windll.user32.GetSystemMetrics(0) - 150 # Recupere longeur écran en pixel - 150
heightGrille = ctypes.windll.user32.GetSystemMetrics(1) - 150 # Recupere largeur écran en pixel - 150
nbCase = 80
PAS = widthGrille // nbCase
listeGrille = list() #Equivaut à deux crochets [] (Instancie une liste)
MARGE = 5
differenceTemps = 0
etatPause = True
tempsPause = 0
paused = 0
ref = time.time() # Fonction du module temps
debut = None


### Initialisation Main ###
root = Tk() # Creation de l'interface
root.iconbitmap('Icone.ico') # Affichage de l'icone en haut à gauche
root.title('Jeu de la vie de Conway') # Affichage du titre personnalisé


### Variables liées au Canvas ###
fond = Canvas(root) # Lié un Canvas à l'interface, c'est à dire la fenêtre principale
grille = Canvas(root, bg="light gray", height=heightGrille, width=widthGrille) # Lie un canvas au root, de couleur gris clair aux dimensions personnalisees

### Fonctions de la grille ###
def nouvelleGrille(mode="normal", liste=None): # Parametres de base
    """Affiche la grille selon le mode : Par défaut charge une grille normale blanche"""
    grille.delete("all")# Supprime tous les objets du Canvas grille
    if mode == "charge":
        for i in range(len(liste)):
            for j in range(len(liste[i])):
                if liste[i][j] == "1": # Si 1 : la case est noire
                    grille.create_rectangle(MARGE+PAS*i,MARGE+PAS*j,MARGE+PAS*(i+1),MARGE+PAS*(j+1),fill="black",outline="black") # .create_rectangle(x1, y1, x2, y2) // Crée le rectangle
                else: # Sinon elle est blanche
                    grille.create_rectangle(MARGE+PAS*i,MARGE+PAS*j,MARGE+PAS*(i+1),MARGE+PAS*(j+1),fill="white",outline="black")
    else:
        liste = list() # Instancie une liste
        for i in range(nbCase):
            ligne = list()
            for j in range(nbCase-38):
                grille.create_rectangle(MARGE+PAS*i,MARGE+PAS*j,MARGE+PAS*(i+1),MARGE+PAS*(j+1),fill="white",outline="black")
                ligne.append("0") # Ajoute à la liste
            liste.append(ligne)
        return liste # Renvoie la grille

def coordonnees(event):
    """Bascule la couleur d'une case après un clic"""
    global listeGrille, nbCells
    print(event.x,event.y,event.x//PAS,event.y//PAS) # Affichage console des coordonnées cliquées + coordonnées réelles
    if listeGrille[int(event.x//PAS)][int(event.y//PAS)] == "0": # Si la case à l'emplacement du clic est morte
        listeGrille[int(event.x//PAS)][int(event.y//PAS)] = "1"
        nbCells+=1
        nbCellsSVar.set(nbCells) # Change le nombre de cellules vivantes
    else:
        listeGrille[int(event.x//PAS)][int(event.y//PAS)] = "0"
        nbCells-=1
        nbCellsSVar.set(nbCells)
    nouvelleGrille("charge", listeGrille) # Crée nouvelle grille

def caseRandom():
    """Colorie de façon aléatoire les cases de la grille"""
    global listeGrille
    if etatPause and differenceTemps == 0: # Si en pause et jeu pas débuté
        for i in range(len(listeGrille)):
            for j in range(len(listeGrille[i])):
                rand = random.randint(0,3) # Aléatoire [0;3]
                if not rand:# Comme ça on obtient une probabilité plus faible de cases noires
                    listeGrille[i][j] = "1"
                else:# Probabilité plus grosse donc blanc (Sinon on a presque que du noir)
                    listeGrille[i][j] = "0"
    nouvelleGrille("charge", listeGrille)
    compteur(listeGrille)

def viderGrille():
    """Vide la grille, reset le timer, arrête le timer, fait afficher 0 au label du temps"""
    global etatPause, differenceTemps, listeGrille, nbCells, jours
    print("Etat Pause :", etatPause) # Affichage console de l'état de pause
    if etatPause: # Si pause on réinitialise toutes les variables
        differenceTemps = 0
        etatPause = True
        nbCells = 0
        jours = 0
        textTemps.set(0) # Modifie la variable du Label textTemps
        joursSVar.set(0)
        nbCellsSVar.set(0)
        listeGrille = list()
        listeGrille = nouvelleGrille()

event = grille.bind("<Button-1>", coordonnees) # Lie le clic gauche au canvas pour une action, lance coordonnées


### Fonctions outils  ###
def miseAJoursTemps():
    """Met à jour la variable du chronometre, met à jour le label qui affiche le temps, fonction récurente"""
    global differenceTemps, tempsPause, ref
    differenceTemps = ((time.time()) - ref) - tempsPause # Temps actuel - temps au démarrage - temps passé en pause
    textTemps.set(round(differenceTemps, 1)) # Modifie la variable du Label textTemps en round() avec un chiffre apres la virgule
    if not etatPause: # Si pas etatPause equivaut a If etatPause==False
        root.after(10, miseAJoursTemps) # Fonction recurrente qui update le temps toute 10 ms

def correctArea(cells, listeGrille):
    """
    Récupère la liste des cellules
    et vérifie si la grille correspond aux attendus
    Pas de chiffres autres que 0 ou 1 ainsi que la taille correspondante
    """
    if not cells or len(cells) != len(listeGrille): # Si liste vide ou que largeur différente
        print("Fichier vide ou grille de mauvaise taille")
        return False # Renvoie le booléen Faux
    for i in range(len(cells)):
        if len(cells[i]) != len(listeGrille[i]): # Si longeur différente
            print("Grille de mauvaise taille") 
            return False # Renvoie le booléen Faux
        for j in range(len(cells[i])):
            if not cells[i][j].isdigit() or int(cells[i][j])>1: # Si caractère alphabètique ou nombre plus grand que 1. Les nombres négatifs ne sont pas à gérer car "-" est un caractère non numérique.
                print("Nombre invalide")
                return False # Renvoie le booléen Faux
    return True # Renvoie le booléen Vrai

def compteur(listeGrille):
    """Compte les cases noires pour le Label correspondant et le met à jour"""
    global nbCells
    nbCells = 0
    for i in range(len(listeGrille)):
        for j in range(len(listeGrille[i])):
            if listeGrille[i][j] == "1": # Si cellule vivante
                nbCells += 1
    nbCellsSVar.set(nbCells) # Modifie la variable du Label nbCellsSVar
    

def listeATexte(listeGrille):
    texte = ""
    for i in range(len(listeGrille)):
        for j in range(len(listeGrille[i])):
            if listeGrille[i][j] == "0": # Si cellule morte
                texte += "0"
            else:
                texte += "1"
        texte += "\n" # Saut de ligne pour le fichier texte de sauvegarde
    return texte

### Fonction des boutons ###
# Gestion du jeu
def demarrer():
    """Initialisation du timer, lance la simulation de la grille"""
    global differenceTemps, etatPause, ref, tempsPause, paused
    if differenceTemps == 0:# Si le jeu n'a pas débuté
        ref = time.time() # Récupère le temps écoulé depuis le premier janvier 1970 (C'est le temps choisi par le module)
        tempsPause = 0
        paused = time.time()
    print("Etat Pause :", etatPause)
    if etatPause: # Si en pause -> if etatPause == True:
        etatPause = False
        tempsPause = tempsPause+(time.time() - paused) # Calcul du temps
        miseAJoursTemps() # Mise à jour du temps
        jeu() # Boucle prinpale du jeu

def jeu():
    global listeGrille, debut, jours
    listeGrille = vie(listeGrille) # Retourne la nouvelle grille
    nouvelleGrille("charge", listeGrille) # Affichage de la nouvelle grille
    jours+=1
    joursSVar.set(jours) # Mise à jour du nombre de jours
    compteur(listeGrille) # Mise à jours du nombre de cases vivantes
    debut = root.after(50, jeu) # Appel récursif de la fonction jeu après 50 ms

def vie(listeGrilleTexte):
    nouveauTour = list()
    for i in range(nbCase): # Boucle créant la matrice de "0"
        nouveauTour.append(["0" for i in range(nbCase-38)])

    for i in range(len(listeGrilleTexte)):
        for j in range(len(listeGrilleTexte[i])):
            nbVoisins = voisins(i, j, listeGrilleTexte) # Récupère le nombre de voisins
            if listeGrilleTexte[i][j] == "1" and nbVoisins < 2: # Suite d'instructions pour vérifier : Si cellule vivante et nombre de voisins < 2 -> Elle meurt
                nouveauTour[i][j] = "0"
            elif listeGrilleTexte[i][j] == "1" and nbVoisins > 3: # Si cellule vivante et nombre de voisins > 3 -> Elle meurt
                nouveauTour[i][j] = "0"
            elif listeGrilleTexte[i][j] == "0" and nbVoisins == 3: # Si cellule morte et nombre de voisins = 3 -> Elle naît
                nouveauTour[i][j] = "1"
            else:
                nouveauTour[i][j] = listeGrilleTexte[i][j] # Sinon rien
    return nouveauTour

def voisins(i, j, listeGrilleTexte):
    total = 0
    tailleLigne = len(listeGrilleTexte) # Taille ligne
    tailleColonne = len(listeGrilleTexte[0]) # Taille colonne
    for k in range(i-1, i+2):
        if k < 0:
            ligne = tailleLigne-1
        elif k > tailleLigne-1:
            ligne = 0
        else:
            ligne = k
        for l in range(j-1, j+2):
            if l < 0:
                colonne = tailleColonne-1
            elif l > tailleColonne-1:
                colonne = 0
            else:
                colonne = l
            # On a alors un couple de coordonnées : (ligne;colonne);(i;j);(k;l)
            if not (ligne == i and colonne == j): # Si les couples (ligne;colonne);(i;j) ne sont pas identiques
                if listeGrilleTexte[ligne][colonne] == "1": # Si cellule vivante aux coordonnées (ligne;colonne)
                    if not (k != ligne or l != colonne): # Equivaut à "if (k == ligne or l == colonne)"
                        total += 1
    return total # Renvoie le total de voisins

# Boutons utiles
def pause():
    """Met en pause le timer ainsi que la simulation"""
    global paused, etatPause, tempsPause, debut
    root.after_cancel(debut) # Annule le dernier .after() contenu dans la variable début
    print("Etat Pause :", etatPause)
    if not etatPause: # Si pas en pause
        etatPause = True # Met en pause
        paused = time.time() # Initialisation du temps début pause

def save():
    """Sauvegarde la grille"""
    global listeGrille
    print("Etat Pause :", etatPause)
    if etatPause and differenceTemps==0: # Si en pause et jeu pas débuté
        directory = loader.asksaveasfile(initialdir=".", title="My GOL", defaultextension=".gol",
                                         filetypes=(('Text files', '*.txt'), ('GOL files', '*.gol'), ('All files', '*.*')))
        # asksaveasfile("."=le dossier du fichier lui meme, "MY GOL"=nom de la fenetre, ".gol"=extension par defaut, filetypes=types de fichiers autorisés)
        # Le tout dans une variable : Si aucun choix effectué (ferme la fenetre) -> variable = None, Sinon variable = True
        if directory: # Si fichier choisi
            texte = listeATexte(listeGrille) # Transfert dans un format texte
            directory.write(texte) # Ecrit dans le fichier
            directory.close() # Ferme le fichier

def load():
    """Ouvre un fichier .gol/.txt et recupere la grille correspondant"""
    global listeGrille
    print("Etat Pause :", etatPause)
    if etatPause and differenceTemps==0: # Si en pause et jeu pas débuté
        filename = loader.askopenfilename(defaultextension='.gol',
                                        filetypes=(('Text files', '*.txt'), ('GOL files', '*.gol'), ('All files', '*.*')))
        # askopenfilename(".gol"=extension par defaut, filetypes=types de fichiers autorisés)
        # Le tout dans une variable : Si aucun choix effectué (ferme la fenetre) -> variable = None, Sinon variable = True
        if not filename: # Si aucun fichier choisi
            return box.showinfo("Erreur", "Aucun fichier sélectionné") # Termine la fonction, c'est à dire qu'on ne lit pas plus loin et on retourne un message d'erreur

        with open(filename, 'r') as file: # Ouvre le fichier en mode lecture texte sous la variable file
            line = None
            listeGrilleTemp = list()
            
            while line != "": # Tant que fichier pas termine
                line = file.readline().strip() # Lit la ligne suivante du fichier et supprime les espaces en trop autour
                listeGrilleTemp.append(list(line))
            del listeGrilleTemp[-1] # C'est une liste vide à l'indice -1, on la supprime donc pour ne pas gêner la vérification

            file.close() # Ferme le fichier

            if not correctArea(listeGrilleTemp, listeGrille): # Appelle la fonction qui verfie la qualite de la grille, retourne un booléen Vrai ou Faux
                return box.showinfo("Erreur", "La grille ne correspond pas aux attentus, elle ne sera pas chargée") # Termine la fonction, c'est à dire qu'on ne lit pas plus loin et on retourne un message d'erreur
            else:
                grille.delete("all") # Supprime l'ancienne grille
                listeGrille = list(listeGrilleTemp) # Copie la liste qu'on vient de vérifier dans la variable appropriée
                nouvelleGrille("charge", listeGrilleTemp) # Création de la nouvelle grille
                compteur(listeGrille) # Mise à jour du compteur de cellules vivantes

def quit():
    root.destroy()

### Definition des labels et boutons, a mettre a jour avec les variables ###
# Nombre de jours
texteJours = Label(fond, text='Nombre de jours\n(Générations)', font=font.Font(family=fontName, size=fontSizeTitle))
joursSVar = StringVar() # Variable Texte Tkinter
joursSVar.set(jours) # Mise à jour de cette variable
varJours = Label(fond, textvariable=joursSVar, font=font.Font(family=fontName, size=fontSizeDesc))

# Nombres de cellules
texteNbCells = Label(fond, text="Nombre de cellules", font=font.Font(family=fontName, size=fontSizeTitle))
nbCellsSVar = StringVar()
nbCellsSVar.set(nbCells)
varNbCells = Label(fond, textvariable=nbCellsSVar, font=font.Font(family=fontName, size=fontSizeDesc))

# Temps écoulé
texteTempsReel = Label(fond, text="Temps écoulé (s)", font=font.Font(family=fontName, size=fontSizeTitle))
textTemps=StringVar()
textTemps.set(0)
varTempsReel = Label(fond, textvariable=textTemps, font=font.Font(family=fontName, size=fontSizeDesc))

# Bouton pour vider la grille
videGrille = Button(fond, text="Vider la grille", command=viderGrille, font=font.Font(family=fontName))

# Bouton pour generer une grille aleatoire
casesrandom = Button(fond, text="Cases aléatoires", command=caseRandom, font=font.Font(family=fontName))

# Bouton pour commence
debut = Button(root, text="Démarrer", command=demarrer, font=font.Font(family=fontName))

# Bouton pour mettre en pause
pose = Button(root, text="Pause", command=pause, font=font.Font(family=fontName))

#Bouton pour quitter
quitButton = Button(root, text="Quitter", command=quit, font=font.Font(family=fontName))

# Bouton pour sauvegarder
sauvegarder = Button(root, text="Sauvegarder", command=save, font=font.Font(family=fontName))

# Bouton pour charger
charger = Button(root, text="Charger", command=load, font=font.Font(family=fontName))

# On place les deux canvas
fond.grid(row=0, column=4)
grille.grid(row=0, column=0, columnspan=3)

### Placement des différents labels et boutons ###
texteJours.grid(row=0, column=0)
varJours.grid(row = 1)
texteNbCells.grid(row=2, column=0)
varNbCells.grid(row=3)
texteTempsReel.grid(row=4, column=0)
varTempsReel.grid(row=5)
videGrille.grid(row=6,column=0)
casesrandom.grid(row=7, column=0)
charger.grid(row=2, rowspan=3, column=0)
sauvegarder.grid(row=2, rowspan = 3, column=1)
debut.grid(row=2, column=2)
pose.grid(row=3, column=2)
quitButton.grid(row=1, column=4)

root.attributes("-fullscreen", True) # Met un plein écran sur le programme

listeGrille = nouvelleGrille() # Création de la grille vide

root.mainloop()
