from math import log10
import random
from matplotlib import pyplot as plt
from esp8266 import *
from methods import methode_partition


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

    methode_partition(
            esps[2],
            reference_nodes(esps),
            distances_aux_references(esps[2], reference_nodes(esps)),
            (0, 0, 10, 10),
        )


def read_csv(file_name):
    esps = []
    with open(file_name, "r") as file:
        for line in file.readlines():
            if line.startswith("#"):
                continue
            line = line.strip("\n")
            morsels = line.split("\t")
            esps.append(build_esp_dict(morsels))
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


if __name__ == "__main__":
    main()
