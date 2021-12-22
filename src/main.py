#!/usr/bin/python3.9
from math import log10
import random
from matplotlib import pyplot as plt
from esp8266 import *
from methods import (
    methode_partition,
    methode_MonteCarlo,
    methode_gradient,
    apply_method,
)
from graphical import plot_reseau, create_fluctuation_video


def plot_power(signals, real_mean, real_sigma):
    """
    Permet de visualiser la distribution des `signals`
    """

    # just to get a quick view into the shape of the distribution
    # does not act as a proof
    freq = frequencies(signals, margin=0.01)
    plt.plot(freq.keys(), freq.values())
    plt.show()


def main():
    """
    Effectue successivement les différentes visualisations requises pour l'étude.
    """
    print("Running ESP8266 positionning simulation")
    # plot_power(get_measures(4096, -55, 1.6))
    # print(read_csv("config-reseau.csv"))
    esps = read_csv("config-reseau.csv")
    power = signal_moyen(esps[0], esps[1])

    # methods_comparison((0, -3, 8, 8), source_file="config-reseau.csv")
    esps, dims = random_set()
    print(f"Parameters: {len(esps)} ESP8266 nodes on a {dims[2]}x{dims[3]} space.")

    methods_comparison(dims, esps=esps)

    # create_fluctuation_video(reference_nodes(esps)[0])


def random_set():
    """
    Génère un jeu d'ESPs dans un espace aléatoire.
    """
    ref_node_count = random.randrange(3, 20)
    node_count = ref_node_count + random.randrange(1, 10)
    width = random.randrange(10, 50)
    height = random.randrange(10, 50)
    dims = (0, 0, width, height)

    esps = []
    for i in range(ref_node_count):
        esps.append(new_esp(i, (0, 0, 5, 5), ref=True))
    for i in range(ref_node_count, node_count):
        esps.append(new_esp(i, (0, 0, 20, 20)))

    return (esps, dims)


def methods_comparison(dims, source_file=None, esps=[]):
    """
    Applique et visualise successivement toutes les méthodes de géolocalisation.

    Nécessite un jeu d'esps qui peut venir d'un fichier source (`source_file`),
    d'une liste d'`esps` ou d'une combinaison des deux. `dims` est la description de l'espace
    dans lequel la simulation se produit. Pour en savoir plus sur `dims` voir `utils.into_corners`
    """

    if source_file is not None:
        try:
            esps.extend(read_csv(source_file))
        except:
            pass

    ref_esps = reference_nodes(esps)
    calibrage_references(ref_esps)

    distances = {}
    for esp in esps:
        if not esp["reference_node"]:
            distances[esp["id"]] = distances_aux_references(esp, ref_esps)

    fig, axs = plt.subplots(3, 4, figsize=(12, 8))

    # graphiques de références, sans application de méthode de détetection
    plot_reseau(ref_esps, dims, "Capteurs de référence", axs[0][0])
    plot_reseau(ref_esps, dims, "Réseau de noeuds", axs[0][1])

    # méthode de partition
    apply_method(esps, ref_esps, distances, dims, methode_partition)
    plot_reseau(esps, dims, "Méthode par partition", axs[0][2])

    # méthode de Monte-Carlo
    apply_method(esps, ref_esps, distances, dims, methode_MonteCarlo)
    plot_reseau(esps, dims, "Méthode de Monté-Carlo", axs[0][3])

    # méthodes de gradient utilisant les divers méthode de calcul de gradient
    (i, j) = (1, 0)

    for method in (
        "Nelder-Mead",
        "Powell",
        "CG",
        "BFGS",
        "L-BFGS-B",
        "TNC",
        "COBYLA",
        "SLSQP",
    ):
        apply_method(esps, ref_esps, distances, dims, methode_gradient, methode=method)
        plot_reseau(esps, dims, f"Méthode du gradient ({method})", axs[i, j])
        j += 1
        if j == 4:
            j = 0
            i += 1

    plt.tight_layout()
    plt.savefig("localisation.png")
    plt.show()


if __name__ == "__main__":
    main()
