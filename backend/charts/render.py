"""Tracé : graphique du cours + les deux moyennes mobiles + flèches achat/vente.

Le tracé est fait EN CODE (déterministe), pas par le LLM. Le LLM ne fera que commenter
l'image plus tard.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # backend non-interactif : on sauvegarde un fichier PNG
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from . import config  # noqa: E402
from .strategy import ma_crossover  # noqa: E402
from .trade import Trade  # noqa: E402


def plot_ma_crossover(
    ticker: str,
    df: pd.DataFrame,
    trades: list[Trade],
    short: int = config.MA_SHORT,
    long: int = config.MA_LONG,
):
    """Trace et sauvegarde le graphique annoté. Renvoie le chemin du PNG."""
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ind = ma_crossover.indicators(df, short, long)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df.index, df["Close"], color="black", lw=0.7, label="Cours")
    ax.plot(ind.index, ind[f"MM{short}"], color="tab:blue", lw=1.1, label=f"MM{short}")
    ax.plot(ind.index, ind[f"MM{long}"], color="tab:orange", lw=1.1, label=f"MM{long}")

    # Marqueurs des trades clôturés : achat (vert) -> vente (rouge).
    for i, t in enumerate(trades):
        ax.scatter(t.entry_date, t.entry_price, marker="^", color="green", s=80, zorder=5,
                   label="Achat (golden cross)" if i == 0 else None)
        ax.scatter(t.exit_date, t.exit_price, marker="v", color="red", s=80, zorder=5,
                   label="Vente (death cross)" if i == 0 else None)

    # Position encore ouverte (golden cross non clôturé) : triangle vert bordé de noir.
    # Affichée pour que le graphique colle aux moyennes, mais exclue des stats.
    open_pos = ma_crossover.open_entry(df, short, long)
    if open_pos is not None:
        d, p = open_pos
        ax.scatter(d, p, marker="^", color="green", edgecolors="black", linewidths=1.5,
                   s=160, zorder=6, label="Achat — position ouverte")

    ax.set_title(f"{ticker} — croisement MM{short}/MM{long}  ({len(trades)} trades)")
    ax.set_ylabel("Prix ($, ajusté)")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)

    out = config.OUTPUT_DIR / f"{ticker}_ma_{short}_{long}.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return out
