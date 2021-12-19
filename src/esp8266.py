from math import log


def path_loss_params_estimation(s1, s2):
    d1, p1 = s1
    d2, p2 = s2

    gamma = p1 - p2 / (10 * log(d2 / d1))
    p0 = (p1 + p2 + 20 * gamma * log((d1 * d2) / (d0 ** 2))) / 2

    return (p0, 1, gamma)
