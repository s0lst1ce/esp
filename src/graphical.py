from utils import *
from matplotlib import pyplot as plt
from matplotlib import axes


def plot_sensors(esps, fig):
    for esp in esps:
        if esp["reference_node"]:
            # green
            color = "g"
        else:
            # blue
            color = "b"
        (x, y) = esp["coordinates"]
        identifier = esp["id"]
        fix.plot(x, y, color + ".")
        fix.text(x, y, identifier)

        if (pos := "predicted_position") in esp:
            fig.plot(*pos, color + ".")
            d = distance((x, y), pos)
            fix.text(x1, y1, f"{identifier} ({d:.2f})")


def plot_reseau(esps, dims, title, fig):
    (x0, y0, width, height) = dims
    fig.set_xlim(x0, x0 + width)
    fig.set_ylim(y0, y0 + height)
    fig.set_title(title)
