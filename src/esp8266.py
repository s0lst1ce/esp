from math import log


def distance(pos0, pos1):
    x0, y0 = pos0
    x1, y1 = pos1
    return sqrt((y1 - y0) ** 2 + (x1 - x0) ** 2)


def path_loss_params_estimation(s1, s2):
    d1, p1 = s1
    d2, p2 = s2

    gamma = p1 - p2 / (10 * log(d2 / d1))
    p0 = (p1 + p2 + 20 * gamma * log((d1 * d2) / (d0 ** 2))) / 2

    return (p0, 1, gamma)


def reference_nodes(esps):
    for esp in esps:
        if esp["reference_node"] == False:
            esps.pop(esp)
    return esps


def deux_plus_proches_voisins(ref_esp, esps):
    ref_pos = ref_esp["coordinates"]
    dist_map = {}
    for esp in esps:
        dist_map[distance(ref_pos, esp["coordinates"])] = esp
    distances = list(dist_map.keys())
    distances.sort()
    return (dist_map[distances[0]], dist_map[distances[1]])


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


def calibrage_references(esps):
    ref_esps = reference_nodes(esps)
    assert len(ref_esps) >= 3, ValueError(
        "At least three reference nodes are needed to calibrate"
    )

    for esp in ref_esps:
        esp1, esp2 = deux_plus_proches_voisins(esp, ref_esps)
        d1 = distance(esp1["coordinates"], esp["coordinates"])
        d2 = distance(esp2["coordinates"], esp["coordinates"])

        sig1 = signal_moyen(esp, esp1)
        sig2 = signal_moyen(esp, esp2)
        (P0, d0, gamma) = path_loss_params_estimation((d1, sig1), (d2, sig2))
        esp["estimated_path_loss_params"] = {"P0": P0, "d0": d0, "gamma": gamma}
