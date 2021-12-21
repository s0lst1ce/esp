from utils import *
from math import log10


def mean_power(distance, loss_params):
    return loss_params["P0"] - 10 * loss_params["gamma"] * log10(distance)


def path_loss_params_estimation(s1, s2):
    d1, p1 = s1
    d2, p2 = s2
    # arbitrarely chosen
    d0 = 1

    gamma = p1 - p2 / (10 * log10(d2 / d1))
    p0 = (p1 + p2 + 20 * gamma * log10((d1 * d2) / (d0 ** 2))) / 2

    return (p0, d0, gamma)


def reference_nodes(esps):
    ref_esps = []
    for esp in esps:
        if esp["reference_node"] == True:
            ref_esps.append(esp)
    return esps


def deux_plus_proches_voisins(ref_esp, esps):
    ref_pos = ref_esp["coordinates"]
    dist_map = {}
    for esp in esps:
        dist_map[distance(ref_pos, esp["coordinates"])] = esp
    distances = list(dist_map.keys())
    distances.sort()
    # we don't take the first element since it would be the distance to itself
    return (dist_map[distances[1]], dist_map[distances[2]])


def signal_moyen(emetteur, receveur, *, epsilon=0.01):
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
            return new_mean
        else:
            mean = new_mean


def calibrage_references(esps):
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
    distances = []
    for ref_esp in ref_esps:
        dist = distance(esp["coordinates"], ref_esp["coordinates"])
        if dist >= 20:
            dist = None
        distances.append(dist)

    return distances


def MSE(pos, ref_esps, distances):
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
    # change to something more random
    pos = random_uniform_pos(dims)
    d0 = 1.0
    P0 = -random.randrange(450, 650) / 10
    gamma = random.randrange(20, 30) / 10
    sigma = random.randrange(100, 200) / 100
    return to_esp(identifier, pos, P0, gamma, sigma, d0=d0, ref=ref)


def to_esp(identifier, pos, P0, gamma, sigma, ref=False, d0=1.0):
    path_loss_params = {"sigma": sigma, "gamma": gamma, "d0": d0, "P0": P0}
    return {
        "path_loss_params": path_loss_params,
        "coordinates": pos,
        "reference_node": ref,
        "id": identifier,
    }


def apply_method(
    esps, ref_esps, distances, dims, methode_interpolation, *args, **kwargs
):
    for esp in esps:
        if not esp["reference_node"]:
            methode_interpolation(
                esp, ref_esps, distances[esp["id"]], dims, *args, **kwargs
            )
