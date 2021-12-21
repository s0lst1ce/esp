from math import sqrt
import random


def distance(pos0, pos1):
    x0, y0 = pos0
    x1, y1 = pos1
    return sqrt((y1 - y0) ** 2 + (x1 - x0) ** 2)


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
