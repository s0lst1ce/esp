from math import sqrt, log10
import random
from matplotlib import pyplot as plt
from esp8266 import *


def get_measures(amount: int, mean, sigma):
    return [random.gauss(mean, sigma) for _ in range(amount)]


def mean_power(distance, loss_params):
    return loss_params["P0"] - 10 * loss_params["gamma"] * log10(distance)


def expectancy(values):
    """
    this is only sort of an expectancy.
    Indeed, although it enventually performs the correct calculation
    it makes use of the specific formula used in this scenario to optimize away the very notion of probability.
    This whole simplification process brings it down to a simple weighted average.
    """
    return sum(values) / len(values)


def variance(values):
    """
    Just as the formula for the expectancy was greatly simplified it is found
    that the variance of the power of the signal is extremely simple. Indeed the power's
    formula depends on but one random variable. Since V[aX+b]=a^2*E[X]=V[X]=sigma^2 and a=1 here
    hence the variance of the power is simply the expectancy
    """
    return expectancy(values)


def frequencies(values, margin=0):
    values.sort()
    freq = {}
    for (val, i) in zip(values, range(len(values))):
        # could be improved with the new pattern matching introduced in python3.10
        if val - margin <= values[i - 1] <= val + margin:
            indices = list(freq.keys())
            indices.sort()
            freq[indices[-1]] += 1
        else:
            freq[val] = 1
    return freq


def signal_moyen(emetteur, receveur, *, epsilon=0.01):
    d = distance(emetteur["coordinates"], receveur["coordinates"])
    # we start we 16 values
    amount = 16

    real_mean = mean_power(d, emetteur["path_loss_params"])
    sigma = emetteur["path_loss_params"]["sigma"]
    signals = get_measures(
        amount,
        real_mean,
        sigma,
    )

    mean = expectancy(signals)

    while True:
        signals.extend(
            get_measures(
                amount,
                real_mean,
                sigma,
            )
        )
        amount *= 2
        new_mean = expectancy(signals)
        if abs(new_mean - mean) <= epsilon:
            # plot_power(signals, real_mean, sigma)
            return new_mean
        else:
            mean = new_mean


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
    print(power)


# TODO build an example dict for the esp8266 as a mind-note


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
