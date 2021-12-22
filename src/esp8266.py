from utils import *
from math import log10


def mean_power(distance, loss_params):
    """
    La puissance moyenne théorique pour un esp de caractéristiques
    `loss_params` (voir la clé "path_loss_params" d'un esp) à une distance
    `distance` d'un autre esp.
    """
    return loss_params["P0"] - 10 * loss_params["gamma"] * log10(distance)


def path_loss_params_estimation(s1, s2):
    """
    Estimation des caractéristiques d'un esp à partir de deux esp de référence.

    `s1` et `s2` sont des tuples de la forme (distance, puissance)
    où distance est la distance entre l'esp étudié et l'esp de référence.
    Puissance est la puissance moyenne reçue par l'esp étudié par l'esp de référence.

    Retourne le triplet de caractéristiques (P0, d0, gamma)
    """
    d1, p1 = s1
    d2, p2 = s2
    # arbitrarely chosen
    d0 = 1

    gamma = p1 - p2 / (10 * log10(d2 / d1))
    p0 = (p1 + p2 + 20 * gamma * log10((d1 * d2) / (d0 ** 2))) / 2

    return (p0, d0, gamma)


def reference_nodes(esps):
    """
    Retoune la liste des esps de référence parmis la liste `esps` d'esps.
    """

    ref_esps = []
    for esp in esps:
        if esp["reference_node"] == True:
            ref_esps.append(esp)
    return esps


def deux_plus_proches_voisins(ref_esp, esps):
    """
    Détermine les deux plus proches voisins de `ref_esp`

    Retourne un tuple contenant ces deux plus proches voisins.
    S'il existe plusieurs voisins à la même disitance, seul l'un d'eux est
    séléctionné.
    """
    ref_pos = ref_esp["coordinates"]
    dist_map = {}
    for esp in esps:
        dist_map[distance(ref_pos, esp["coordinates"])] = esp
    distances = list(dist_map.keys())
    distances.sort()
    # we don't take the first element since it would be itslef
    # indeed the distance to oneself is always 0
    return (dist_map[distances[1]], dist_map[distances[2]])


def signal_moyen(emetteur, receveur, *, epsilon=0.01):
    """
    Détermine le signal moyen reçu par `receveur` et émis par `emetteur`

    La tolérance est fixée à `epsilon`.
    """
    d = distance(emetteur["coordinates"], receveur["coordinates"])
    # we start we 16 values
    amount = 16

    real_mean = mean_power(d, emetteur["path_loss_params"])
    sigma = emetteur["path_loss_params"]["sigma"]
    signals = get_signals(
        amount,
        real_mean,
        sigma,
    )

    mean = expectancy(signals)

    while True:
        signals.extend(
            get_signals(
                amount,
                real_mean,
                sigma,
            )
        )
        amount *= 2
        new_mean = expectancy(signals)
        if abs(new_mean - mean) <= epsilon:
            # plot_power(signals, real_mean, sigma)
            # print(amount / 2)
            return new_mean
        else:
            mean = new_mean


def calibrage_references(esps):
    """
    Calibre parmis `esps` les esps de référence entre eux.

    Cette fonction modifie les esps en place.
    """
    ref_esps = reference_nodes(esps)
    assert len(ref_esps) >= 3, "At least three reference nodes are needed to calibrate"

    for esp in ref_esps:
        esp1, esp2 = deux_plus_proches_voisins(esp, ref_esps)
        d1 = distance(esp1["coordinates"], esp["coordinates"])
        d2 = distance(esp2["coordinates"], esp["coordinates"])

        sig1 = signal_moyen(esp, esp1)
        sig2 = signal_moyen(esp, esp2)
        (P0, d0, gamma) = path_loss_params_estimation((d1, sig1), (d2, sig2))
        esp["estimated_path_loss_params"] = {"P0": P0, "d0": d0, "gamma": gamma}


def distances_aux_references(esp, ref_esps):
    """
    La distance de `esp` à l'ensemble des esps de référence (`ref_esps`)

    Si la diistance entre l'esp étudié et un esp de référence est supérieure
    à 20m, la distance est plutôt fixée à `None` car il n'est plus possible
    de considérer les mesures comme fiables.

    Retourne une liste des distances, chaque élément correspondant à la distance entre `esp`
    et l'élément de même indice de `ref_esps`.
    """
    distances = []
    for ref_esp in ref_esps:
        dist = distance(esp["coordinates"], ref_esp["coordinates"])
        if dist >= 20:
            dist = None
        distances.append(dist)

    return distances


def MSE(pos, ref_esps, distances):
    """
    Carré de l'écart entre les distances mesurées et les distances attendues.

    Cette fonction est utiile dans le contexte des méthode de géolocalisation
    où elle sert à attribuer un score aux estimations successives. Elle sert donc
    de guide pour le déplacement des points (donc des esps) auxquelles procèdent les
    méthodes (c.f. `methods.py`).

    `pos` représente la position de l'esp étudié
    `ref_esps` est une liste de l'ensemble des noeuds de référence
    `distance` représente la distance entre l'esp en `pos` et les esps de référence
    Ces deux dernières listes doivent être ordonnées identiquement, voir `distances_aux_references`
    pour plus d'information.

    Retourne le score, soit le carré de la différence entre la valeur attendue et la valeur mesurée.
    Si tout les esps sont trop loin de `esp`, retourne -1.0.
    """
    assert (node_nbr := len(ref_esps)) == len(
        distances
    ), "ref_esps and distances must have as many elements, and have the same order"

    count = 0
    score = 0
    for i in range(node_nbr):
        ref_esp = ref_esps[i]
        real_distance = distances[i]
        if real_distance is not None:
            measured_distance = distance(pos, ref_esp["coordinates"])
            score += (real_distance - measured_distance) ** 2
            count += 1

    try:
        score /= count
    # if all distances were `None` then the count is 0, hence the exception
    # we then use -1.0 as the dummy value to denote the incapacity to calculate the MSE
    except ZeroDivisionError:
        score = -1.0

    return score


def new_esp(identifier, dims, ref=False):
    """
    Créé un esp de caractéristiques aléatoires dans l'espace `dim`

    Nécessite l'identifiant (`identfier`) de l'esp ainsi que `ref` pour savoir
    s'il est de référence ou non.

    Retourne un dictionnaire représentant le nouvel esp.
    """
    # we could change to something more random but this way
    # we get sets that are easier to display on a plot and we retain
    # very sensible results
    pos = random_uniform_pos(dims)
    d0 = 1.0
    P0 = -random.randrange(450, 650) / 10
    gamma = random.randrange(200, 300) / 100
    # we prefer to simply create a sensible sigma rather than
    # calculate it through `variance` (afterall V[P]=sigma^2)
    # since it would require generating a heap of values
    sigma = random.randrange(100, 200) / 100
    return to_esp(identifier, pos, P0, gamma, sigma, d0=d0, ref=ref)


def to_esp(identifier, pos, P0, gamma, sigma, ref=False, d0=1.0):
    """
    Construit le dictionnaire représentant l'esp.
    """
    path_loss_params = {"sigma": sigma, "gamma": gamma, "d0": d0, "P0": P0}
    return {
        "path_loss_params": path_loss_params,
        "coordinates": pos,
        "reference_node": ref,
        "id": identifier,
    }
