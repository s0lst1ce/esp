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
    print("all is well")
    # plot_power(256, -55, 1.6)
    # print(read_csv("config-reseau.csv"))
    esps = read_csv("config-reseau.csv")
    power = signal_moyen(esps[0], esps[1])

    setup((0, -3, 8, 8), source_file="config-reseau.csv")


def read_csv(file_name):
    esps = []
    try:
        with open(file_name, "r") as file:
            for line in file.readlines():
                if line.startswith("#"):
                    continue
                line = line.strip("\n")
                morsels = line.split("\t")
                esps.append(build_esp_dict(morsels))
    except Exception as e:
        print("Could not find file : ", file_name)
        raise e
    return esps


def build_esp_dict(morsels):
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


def setup(dims, source_file=None, esps=[]):
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
