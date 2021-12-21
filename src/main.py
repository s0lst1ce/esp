#!/usr/bin/python3.9
from math import log10
import random
from matplotlib import pyplot as plt
from esp8266 import *
from methods import methode_partition, methode_MonteCarlo, methode_gradient
from graphical import plot_reseau


def plot_power(signals, real_mean, real_sigma):
    # just to get a quick view into the shape of the distribution
    # does not act as a proof
    freq = frequencies(signals, margin=0.01)
    plt.plot(freq.keys(), freq.values())
    plt.show()


def main():
    print("Running ESP8266 positionning simulation")
    # plot_power(256, -55, 1.6)
    # print(read_csv("config-reseau.csv"))
    esps = read_csv("config-reseau.csv")
    power = signal_moyen(esps[0], esps[1])

    methods_comparison((0, -3, 8, 8), source_file="config-reseau.csv")
    esps, dims = random_set()
    methods_comparison(dims, esps=esps)


def random_set():
    ref_node_count = random.randrange(3, 20)
    node_count = ref_node_count + random.randrange(1, 10)
    width = random.randrange(10, 50)
    height = random.randrange(10, 50)
    dims = (0, 0, width, height)

    esps = []
    for i in range(ref_node_count):
        esps.append(new_esp(i, dims, ref=True))
    for i in range(ref_node_count, node_count):
        esps.append(new_esp(i, dims))

    return (esps, dims)


def methods_comparison(dims, source_file=None, esps=[]):
    if source_file is not None:
        try:
            esps.extend(read_csv(source_file))
        except:
            pass

    ref_esps = reference_nodes(esps)
    calibrage_references(ref_esps)
    # change this part so that it works for any number of non-reference esps
    # and when we don't know its position in the list
    distances = distances_aux_references(esps[2], ref_esps)
    fig, axs = plt.subplots(3, 4, figsize=(12, 8))

    # graphiques de références, sans application de méthode de détetection
    plot_reseau(ref_esps, dims, "Capteurs de référence", axs[0][0])
    plot_reseau(ref_esps, dims, "Réseau de noeuds", axs[0][1])

    # méthode de partition
    methode_partition(esps[2], ref_esps, distances, dims)
    plot_reseau(ref_esps, dims, "Méthode par partition", axs[0][2])

    # méthode de Monte-Carlo
    methode_MonteCarlo(esps[2], ref_esps, distances, dims)
    plot_reseau(ref_esps, dims, "Méthode de Monté-Carlo", axs[0][3])

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
        methode_gradient(esps[2], ref_esps, distances, dims, methode=method)
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
