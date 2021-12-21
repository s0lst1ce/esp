from utils import *
from esp8266 import MSE
import random
from scipy import optimize as opti

# FIXME what is all MSE return -1? We'll have wrong values


def methode_partition(esp, ref_esps, distances, dims, *, epsilon=0.01):
    if dims[2] * dims[3] < epsilon:
        esp["predicted_position"] = middle_rect(dims)

    else:
        corners = into_corners(dims)

        min_mse = None
        matching_corner = None
        for corner, i in zip(corners, range(4)):
            mse = MSE((pos := (corner[0], corner[1])), ref_esps, distances)
            if (min_mse is None) or (min_mse > mse):
                min_mse = mse
                matching_corner = i

        if min_mse == 0:
            esp["predicted_position"] = pos
        else:
            methode_partition(
                esp, ref_esps, distances, corners[matching_corner], epsilon=epsilon
            )


def methode_MonteCarlo(
    esp, ref_esps, distances, dims, *, epsilon=0.01, nb_tirages=None
):
    (x0, y0, width, height) = dims

    if width * height < epsilon:
        esp["predicted_position"] = middle_rect(dims)
        return None

    if nb_tirages is None:
        # jspas quel choix a le plus de sens :shrug:
        points_nbr = max(width, height)

    assert points_nbr > 0, "Width and height must be greater than 0"

    min_mse = None
    matching_pos = None
    for _ in range(points_nbr):
        pos = random_uniform_pos(dims)
        mse = MSE(pos, ref_esps, distances)
        if (min_mse is None) or (min_mse > mse):
            min_mse = mse
            matching_pos = pos

    if min_mse == 0:
        eps["predicted_position"] = min_pos
    else:
        methode_MonteCarlo(
            esp,
            ref_esps,
            distances,
            # on créé un rectangle autour du point avec la meilleure MSE
            (
                matching_pos[0] - width / 4,
                matching_pos[1] - height / 4,
                width / 2,
                height / 2,
            ),
            epsilon=epsilon,
            nb_tirages=nb_tirages,
        )


def methode_gradient(
    esp, ref_esps, distances, dims, *, epsilon=0.01, methode="L-BFGS-B"
):
    (x0, y0, width, height) = dims
    if width * height < epsilon:
        esp["predicted_position"] = middle_rect(dims)
    else:
        # starting from the middle of the space we use the MSE
        # as the scoring function to orient the gradient
        outcome = opti.minimize(
            lambda pos: MSE(pos, ref_esps, distances), middle_rect(dims), method=methode
        )

        if outcome.success:
            esp["predicted_position"] = (rex.x[0], res.x[1])
        else:
            esp["predicted_position"] = random_uniform_pos(dims)
