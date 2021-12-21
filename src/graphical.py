from utils import *
from matplotlib import pyplot as plt
from matplotlib import axes
import progressbar as pb


def plot_sensors(esps, fig):
    for esp in esps:
        if esp["reference_node"]:
            # green
            color = "g"
        else:
            # blue
            color = "b"
        identifier = esp["id"]
        (x, y) = esp["coordinates"]

        if "predicted_position" in esp:
            pos = esp["predicted_position"]
            fig.plot(*pos, color + ".")
            d = distance((x, y), pos)
            fig.text(*pos, f"{identifier} ({d:.2f})")
        else:
            fig.plot(x, y, color + ".")
            fig.text(x, y, identifier)


def plot_reseau(esps, dims, title, fig):
    (x0, y0, width, height) = dims
    fig.set_xlim(x0, x0 + width)
    fig.set_ylim(y0, y0 + height)
    fig.set_title(title)
    plot_sensors(esps, fig)


def animation(frame, esp, data, limit):
    pass


def show_progress(frame, total_frames):
    pbx.update(frame)
