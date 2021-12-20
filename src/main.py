import random
from matplotlib import pyplot as plt
from esp8266 import path_loss_params_estimation


def get_measures(amount: int, mean, sigma):
    return [random.gauss(mean, sigma) for _ in range(amount)]


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
    pass


def plot_power(amount, real_mean, real_sigma):
    # WIP, just for testing atm
    values = get_measures(amount, real_mean, real_sigma)
    freq = frequencies(values, margin=0.1)
    plt.plot(freq.keys(), freq.values())
    plt.show()


def main():
    print("all is well")
    plot_power(256, -55, 1.6)


# TODO build an example dict for the esp8266 as a mind-note


def read_csv(file_name):
    pass


def sqrt(value):
    pass


if __name__ == "__main__":
    main()
