from utils import *
from matplotlib import pyplot as plt
from matplotlib import animation as anm
from matplotlib import axes
import progressbar as pbar


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


def animation(frame, esp, data, limit, fig):
    ax = fig.axes[0]
    ax.clear()
    ax.set_xlim([0, limit])
    ax.set_ylim([-100, 0])
    ax.set_title(f"""Force du signal de l'ESP8266 n°{esp["id"]}""")
    ax.set_ylabel("dBm")
    for (distance, c, signals) in data:
        F = get_signal_from_esp(esp, distance)
        signals.append(F)
        # truncate view to the latest values
        signals = signals[-limit:]
        # update view buffer for the frame
        ax.plot(signals, c + "-", label=f"distance: {distance}m")

    ax.legend()


def create_fluctuation_video(ref_node, out_file="animation.mp4"):
    fig, ax = plt.subplots()

    # curves settings
    curves_colors = ["r", "b", "g", "c", "m", "y"]
    curves_data = [(2 ** i, curves_colors[i], []) for i in range(len(curves_colors))]

    # video settings
    duration = 10.0  # in seconds
    fps = 30
    frames_count = int(duration * fps)

    vid = anm.FuncAnimation(
        fig,
        animation,
        fargs=(ref_node, curves_data, frames_count // 2, fig),
        frames=frames_count,
        interval=1000 / fps,
        repeat=False,
    )

    plt.tight_layout()

    pbar_elts = [
        f"""Enregistrement de la simulation dans {out_file} [{pbar.SimpleProgress(sep="/")}] {pbar.Timer(format="Temps écoulé: {}")} {pbar.AnimatedMarker(markers="/-|")} {pbar.Bar(left="[", right="]", fill="-", marker="=")} {pbar.ETA()} {pbar.Percentage()})"""
    ]
    pb = pbar.ProgressBar(widgets=pbar_elts, maxval=frames_count)

    # recoding
    pb.start()
    vid.save(out_file, progress_callback=lambda *args: pb.update(args[0]), fps=fps)
    pb.finish()

    plt.show()


def show_progress(frame, total_frames):
    # how to pass pb to it????
    pbar.update(frame)
