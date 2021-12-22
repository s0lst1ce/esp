# Méthode de g.olocalisation
# L'explicaton de leur fonctionnement peut être trouvé dans le rapport.

from utils import *
from esp8266 import MSE
import random
from scipy import optimize as opti


def methode_partition(esp, ref_esps, distances, dims, *, epsilon=0.01):
    """
    détermination de la position par méthode des partitions (ici itération d'une grille 2x2)
    """
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

        if min_mse == -1:
            raise ValueError(
                "All reference esps were too far from `esp`, hence the method couldn't be applied"
            )
        if min_mse == 0:
            esp["predicted_position"] = pos
        else:
            methode_partition(
                esp, ref_esps, distances, corners[matching_corner], epsilon=epsilon
            )


def methode_MonteCarlo(
    esp, ref_esps, distances, dims, *, epsilon=0.01, nb_tirages=None
):
    """
    détermination de la position par méthode de Monte-Carlo
    """
    (x0, y0, width, height) = dims

    if width * height < epsilon:
        esp["predicted_position"] = middle_rect(dims)
        return None

    if nb_tirages is None:
        points_nbr = int(max(width, height)) + 1

    assert (
        points_nbr > 0
    ), f"Width and height must be greater than 0, got {width}, {height}"

    min_mse = None
    matching_pos = None
    for _ in range(points_nbr):
        pos = random_uniform_pos(dims)
        mse = MSE(pos, ref_esps, distances)
        if (min_mse is None) or (min_mse > mse):
            min_mse = mse
            matching_pos = pos

    if min_mse == -1:
        raise ValueError(
            "All reference esps were too far from `esp`, hence the method couldn't be applied"
        )
    if min_mse == 0:
        esp["predicted_position"] = min_pos
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
    """
    détermination de la position par les dérivées numériques calculées avec la méthode `methode`"
    """
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
            esp["predicted_position"] = (outcome.x[0], outcome.x[1])
        else:
            esp["predicted_position"] = random_uniform_pos(dims)


def apply_method(
    esps, ref_esps, distances, dims, methode_interpolation, *args, **kwargs
):
    """
    Applique `methode_interpolation` à tout les `ESPs`.
    """
    for esp in esps:
        if not esp["reference_node"]:
            methode_interpolation(
                esp, ref_esps, distances[esp["id"]], dims, *args, **kwargs
            )
