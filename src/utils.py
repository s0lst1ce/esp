# Ce module fournit un ensemble de méthodes utiles à l'ensemble des autres
# modules du projet. Elle ne contient que les fonctions indépendantes des esp
# ainsi que des algoruithmes de géolocalisation.

from math import sqrt, log10
import random


def read_csv(file_name):
    """
    Lit un le fichier `file_name` et l'interprète comme un CSV afin de
    construire une liste de dictionnaires représentant des esp8266.

    Affiche un message d'erreur si le fichier n'existe pas et propage l'erreur.
    """
    esps = []
    try:
        with open(file_name, "r") as file:
            for line in file.readlines():
                if line.startswith("#"):
                    continue
                line = line.strip("\n")
                morsels = line.split("\t")
                esps.append(esp_from_string(morsels))
    except Exception as e:
        print("Could not find file : ", file_name)
        raise e
    return esps


def esp_from_string(morsels):
    """
    Construit un esp à partir d'une liste de str représentant les caractéristiques de l'esp.

    `morsels` est une liste de chaîne de charactères dont les éléments représentent dans l'ordre:
    - sigma
    - gamma
    - d0
    - P0
    - coordinates (la position de l'esp)
    - reference_node (si l'esp est un noeud de référence)
    - id (l'identifiant entier de l'esp)
    """

    path_loss_params = {}
    path_loss_params["sigma"] = float(morsels.pop())
    path_loss_params["gamma"] = float(morsels.pop())
    path_loss_params["d0"] = float(morsels.pop())
    path_loss_params["P0"] = float(morsels.pop())

    esp = {"path_loss_params": path_loss_params}
    y, x = float(morsels.pop()), float(morsels.pop())
    esp["coordinates"] = (x, y)

    is_true = lambda val: val == "True"
    esp["reference_node"] = is_true(morsels.pop())
    esp["id"] = int(morsels.pop())
    return esp


def distance(pos0, pos1):
    """
    Distance euclidienne entre `pos0` et `pos1`.

    Les deux arguments sont des tuples (x, y) dont les composantes (des floats) sont
    les coordonnées selon les abscisses et ordonnées du plans, respectivement.
    """

    x0, y0 = pos0
    x1, y1 = pos1
    # distance euclidienne
    return ((y1 - y0) * (y1 - y0) + (x1 - x0) * (x1 - x0)) ** 0.5


def get_signals(amount: int, mean, sigma):
    """
    Génère `amount` signaux.

    Cette fonction ne sert que pour la simulation. Dans une situation pratique,
    elle serait remplacé par un driver qui interagirait avec l'esp pour relever
    des mesures de signaux.
    Faute d'esp, il existe cette fonction qui simule des signaux avec un bruits variable.
    Cette variation (dictée par `sigma`) des signaux suit une loi normale (distribution gaussienne) centrée sur `mean`.
    """

    # valeurs aléatoires sur une distribution gaussienne
    return [random.gauss(mean, sigma) for _ in range(amount)]


def get_signal_from_esp(esp, distance):
    """
    Génère un signal à partir des caractéristiques de `esp`.

    Les modalités de génération du signal sont les mêmes que pour `get_signals`
    """
    params = esp["path_loss_params"]
    P0 = params["P0"]
    d0 = params["d0"]
    gamma = params["gamma"]
    sigma = params["sigma"]

    return P0 - 10 * gamma * log10(distance / d0) + random.gauss(0, sigma)


def expectancy(values):
    """
    L'espérance d'un ensemble de puissances.

    La formulation générale de l'espérance implique des probabilités et procède à
    une moyenne pondérée. Seulement ici elle ne sert qu'à l'obtention de la puissance moyenne des signaux.
    Au vue de l'expression des dites puissances, il est possible de grandement simplifier l'expression de
    l'espérance. Ainsi dans notre cas elle est équivalente à une simple moyenne.
    """

    return sum(values) / len(values)


def variance(values):
    """
    La variance d'un ensemble de puissances.

    On procède a des simplification, comme pour l'espérance. Se référer au compte-rendu pour
    une explication détaillée des simplifications.
    """

    return expectancy([val ** 2 for val in values]) - expectancy(values) ** 2


def frequencies(values, margin=0.01):
    """
    Trie les valeurs par fréquence.

    Cette fonction retourne un dictionnaire représentant la distribution des signaux.
    `margin` représente la tolérance à partir de laquelle deux valeurs sont considérées identiques.
    """

    freq = {}
    for value in values:
        if margin != 0:
            value = value // margin * margin
        freq[value] = freq.get(value, 0) + 1
    return freq


def into_corners(dims):
    """
    Divise l'espace `dims`, supposé rectangulaiire, en 4 coins égaux.

    `dims` se présente comme un tuple de 4 floats représentant respectivement:
    - la coordonnée des abscisses du point supérieur gauche de l'espace
    - la coordonnée des ordonnées du point supérieur gauche de l'espace
    - la largeur de l'espace
    - la heuteur de l'espace (ou la longeur suivant la perception, le calcul reste inchangé)

    La fonction retourne un tuple de quater coins de même structure que `dims`
    """

    (x0, y0, width, height) = dims
    corners = []
    for i in range(2):
        for j in range(2):
            x, y = x0 + i * width / 2, y0 + j * height / 2
            w, h = width / 2, height / 2
            corners.append((x, y, w, h))
    return corners


def middle_rect(dims):
    """
    Le milieu d'un espace rectangulaire
    """
    (x0, y0, width, height) = dims
    return (x0 + width / 2, y0 + height / 2)


def random_uniform_pos(dims):
    """
    Une position aléatoire mais suivant une loi de distribution uniforme.

    Utile pr créé un nuage de points équitablement répartis ds un espace.

    Retourne un tuple de floats.
    """
    (x0, y0, width, height) = dims
    return (random.uniform(x0, x0 + width), random.uniform(y0, y0 + height))
