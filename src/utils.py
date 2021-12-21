from math import sqrt
import random


def read_csv(file_name):
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
    x0, y0 = pos0
    x1, y1 = pos1
    # distance euclidienne
    return ((y1 - y0) * (y1 - y0) + (x1 - x0) * (x1 - x0)) ** 0.5


def get_measures(amount: int, mean, sigma):
    # valeurs aléatoires sur une distribution gaussienne
    return [random.gauss(mean, sigma) for _ in range(amount)]


def expectancy(values):
    """
    this is only sort of an expectancy.
    Indeed, although it enventually performs the correct calculation
    it makes use of the specific formula used in this scenario to optimize away the very notion of probability.
    This whole simplification process brings it down to a simple weighted average.

    L'espérance est tout simplement la moyenne des puissances du signal
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
    freq = {}
    for value in values:
        if margin != 0:
            value = value // margin * margin
        freq[value] = freq.get(value, 0) + 1
    return dict(sorted(freq.items()))


def into_corners(dims):
    (x0, y0, width, height) = dims
    corners = []
    for i in range(2):
        for j in range(2):
            x, y = x0 + i * width / 2, y0 + j * height / 2
            w, h = width / 2, height / 2
            corners.append((x, y, w, h))
    return corners


def middle_rect(dims):
    (x0, y0, width, height) = dims
    return (x0 + width / 2, y0 + height / 2)


def random_uniform_pos(dims):
    (x0, y0, width, height) = dims
    return (random.uniform(x0, x0 + width), random.uniform(y0, y0 + height))
