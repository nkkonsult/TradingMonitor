"""Stratégie : épaule-tête-épaule (head & shoulders) — figure chartiste géométrique.

Deux variantes via le paramètre `direction` (déclarées 2x dans le registre) :
- "bearish" (classique) : 3 SOMMETS (épaule G, tête plus haute, épaule D), cassure
  de la ligne de cou VERS LE BAS -> signal baissier -> trade SHORT (direction=-1).
- "bullish" (inversé)   : 3 CREUX (miroir), cassure VERS LE HAUT -> achat -> LONG (+1).

Détection 100 % déterministe (extrema locaux + conditions géométriques chiffrées) ->
reproductible -> stats valides. Le LLM n'intervient pas. C'est la figure "vitrine" :
RARE, donc peu de trades sur un seul titre -> trancher sur tout le S&P 500.

Pour chaque figure validée on définit, comme un vrai trader :
- entrée = cassure de la ligne de cou après l'épaule droite ;
- objectif (take-profit) = "measured move" = hauteur tête<->cou reportée depuis la cassure ;
- stop = au-delà de l'épaule droite (la figure est invalidée).
Le trade est clôturé au PREMIER des deux atteint (objectif ou stop). Une figure dont
ni l'objectif ni le stop ne se réalisent avant la fin des données n'est pas comptée.
"""
from __future__ import annotations

import pandas as pd

from ..trade import Trade

# Défauts (chiffrent la figure sans ambiguïté ; figer pour la reproductibilité).
PIVOT_WINDOW = 10       # un extremum doit dominer +/- 10 jours -> vraies grandes oscillations
SHOULDER_TOL = 0.05     # écart max de hauteur entre les deux épaules (5 % de la tête)
MIN_PROMINENCE = 0.03   # la tête doit dépasser les épaules d'au moins 3 %
TIME_SYMMETRY = 0.5     # symétrie temporelle : la + courte moitié >= 50 % de la + longue
NECKLINE_LEVEL_TOL = 0.06  # ligne de cou ~horizontale : 2 points de cou à <= 6 % l'un de l'autre
BREAK_HORIZON = 60      # jours max après l'épaule droite pour voir la cassure
TRADE_HORIZON = 252     # jours max après la cassure pour atteindre objectif/stop


def _pivots(vals, w: int) -> list[tuple[int, int]]:
    """Extrema locaux -> liste (position, kind) avec kind +1 sommet / -1 creux.

    Nettoie ensuite les pivots consécutifs de même type en gardant le plus extrême,
    pour obtenir une alternance sommet/creux (façon zig-zag)."""
    raw: list[tuple[int, int]] = []
    n = len(vals)
    for i in range(w, n - w):
        seg = vals[i - w : i + w + 1]
        if vals[i] == seg.max() and seg.argmax() == w:
            raw.append((i, 1))
        elif vals[i] == seg.min() and seg.argmin() == w:
            raw.append((i, -1))

    clean: list[tuple[int, int]] = []
    for p in raw:
        if clean and clean[-1][1] == p[1]:
            prev = clean[-1]
            more_extreme = (p[1] == 1 and vals[p[0]] > vals[prev[0]]) or (
                p[1] == -1 and vals[p[0]] < vals[prev[0]]
            )
            if more_extreme:
                clean[-1] = p
        else:
            clean.append(p)
    return clean


def _neckline(t1: int, n1: float, t2: int, n2: float):
    """Droite de cou passant par les deux creux/sommets de cou (interpolée/extrapolée)."""
    slope = (n2 - n1) / (t2 - t1) if t2 != t1 else 0.0
    return lambda pos: n1 + slope * (pos - t1)


def _scan(
    df: pd.DataFrame,
    direction: str,
    pivot_window: int,
    shoulder_tol: float,
    min_prominence: float,
    break_horizon: int,
    trade_horizon: int,
    time_symmetry: float,
    neckline_level_tol: float,
) -> list[dict]:
    """Cœur de détection : renvoie un enregistrement RICHE par figure clôturée.

    Chaque dict porte le trade ET la géométrie (pivots, ligne de cou, objectif) pour
    que detect_trades (stats) et shapes (tracé) partagent exactement la même logique.
    """
    vals = df["Close"].to_numpy()
    idx = df.index
    n = len(vals)
    bullish = direction == "bullish"
    d = 1 if bullish else -1

    piv = _pivots(vals, pivot_window)
    # Séquence extrême-cou-extrême-cou-extrême :
    # bearish : sommet,creux,sommet,creux,sommet (start kind = +1)
    # bullish : creux,sommet,creux,sommet,creux (start kind = -1)
    start_kind = -1 if bullish else 1

    out: list[dict] = []
    last_exit_pos = -1

    for k in range(len(piv) - 4):
        window = piv[k : k + 5]
        if window[0][1] != start_kind:
            continue
        (s1, _), (c1, _), (head, _), (c2, _), (s3, _) = window  # positions
        p_s1, p_head, p_s3 = vals[s1], vals[head], vals[s3]
        p_c1, p_c2 = vals[c1], vals[c2]

        if bullish:
            # 3 creux : tête (head) la plus BASSE, épaules comparables au-dessus.
            if not (p_head < p_s1 and p_head < p_s3):
                continue
            if abs(p_s1 - p_s3) > shoulder_tol * abs(p_head):
                continue
            if (p_s1 - p_head) / p_s1 < min_prominence or (p_s3 - p_head) / p_s3 < min_prominence:
                continue
        else:
            # 3 sommets : tête la plus HAUTE, épaules comparables en-dessous.
            if not (p_head > p_s1 and p_head > p_s3):
                continue
            if abs(p_s1 - p_s3) > shoulder_tol * abs(p_head):
                continue
            if (p_head - p_s1) / p_head < min_prominence or (p_head - p_s3) / p_head < min_prominence:
                continue

        # Symétrie temporelle : épaule gauche et droite à distance comparable de la tête.
        left_span, right_span = head - s1, s3 - head
        if min(left_span, right_span) < time_symmetry * max(left_span, right_span):
            continue
        # Ligne de cou ~horizontale : les 2 points de cou doivent être à des niveaux proches.
        if abs(p_c2 - p_c1) / max(p_c1, p_c2) > neckline_level_tol:
            continue

        neck = _neckline(c1, p_c1, c2, p_c2)
        head_height = abs(p_head - neck(head))  # amplitude tête <-> cou

        # Cassure de la ligne de cou après l'épaule droite.
        break_pos = None
        for pos in range(s3 + 1, min(s3 + 1 + break_horizon, n)):
            line = neck(pos)
            if (bullish and vals[pos] > line) or (not bullish and vals[pos] < line):
                break_pos = pos
                break
        if break_pos is None or break_pos <= last_exit_pos:
            continue

        entry_price = float(vals[break_pos])
        target = entry_price + d * head_height          # objectif (measured move)
        stop = float(p_s3)                              # épaule droite = invalidation

        # Sortie : 1er jour où l'objectif OU le stop est touché (sur la clôture).
        exit_pos = None
        for pos in range(break_pos + 1, min(break_pos + 1 + trade_horizon, n)):
            c = vals[pos]
            hit_target = (bullish and c >= target) or (not bullish and c <= target)
            hit_stop = (bullish and c <= stop) or (not bullish and c >= stop)
            if hit_target or hit_stop:
                exit_pos = pos
                break
        if exit_pos is None:
            continue  # ni objectif ni stop avant la fin -> figure non comptée

        out.append(
            {
                "direction": d,
                "entry_pos": break_pos,
                "entry_price": entry_price,
                "exit_pos": exit_pos,
                "exit_price": float(vals[exit_pos]),
                "target": float(target),
                # Géométrie pour le tracé : la ligne de cou tracée de l'épaule G à la sortie.
                "neck_left": (s1, float(neck(s1))),
                "neck_right": (exit_pos, float(neck(exit_pos))),
                "head": (head, float(p_head)),
                "shoulders": [(s1, float(p_s1)), (s3, float(p_s3))],
            }
        )
        last_exit_pos = exit_pos

    return out


def detect_trades(
    df: pd.DataFrame,
    *,
    direction: str = "bullish",
    pivot_window: int = PIVOT_WINDOW,
    shoulder_tol: float = SHOULDER_TOL,
    min_prominence: float = MIN_PROMINENCE,
    time_symmetry: float = TIME_SYMMETRY,
    neckline_level_tol: float = NECKLINE_LEVEL_TOL,
    break_horizon: int = BREAK_HORIZON,
    trade_horizon: int = TRADE_HORIZON,
    **_,
) -> list[Trade]:
    """Détecte les figures et renvoie les trades clôturés (objectif ou stop atteint)."""
    idx = df.index
    recs = _scan(df, direction, pivot_window, shoulder_tol, min_prominence,
                 break_horizon, trade_horizon, time_symmetry, neckline_level_tol)
    return [
        Trade(idx[r["entry_pos"]], r["entry_price"], idx[r["exit_pos"]], r["exit_price"], direction=r["direction"])
        for r in recs
    ]


def shapes(
    df: pd.DataFrame,
    *,
    direction: str = "bullish",
    pivot_window: int = PIVOT_WINDOW,
    shoulder_tol: float = SHOULDER_TOL,
    min_prominence: float = MIN_PROMINENCE,
    time_symmetry: float = TIME_SYMMETRY,
    neckline_level_tol: float = NECKLINE_LEVEL_TOL,
    break_horizon: int = BREAK_HORIZON,
    trade_horizon: int = TRADE_HORIZON,
    **_,
) -> list[dict]:
    """Géométrie des figures pour le tracé : ligne de cou, objectif, tête, épaules."""
    idx = df.index
    fmt = lambda pos: idx[pos].strftime("%Y-%m-%d")  # noqa: E731
    recs = _scan(df, direction, pivot_window, shoulder_tol, min_prominence,
                 break_horizon, trade_horizon, time_symmetry, neckline_level_tol)
    out = []
    for r in recs:
        out.append(
            {
                "neckline": [
                    {"date": fmt(r["neck_left"][0]), "price": round(r["neck_left"][1], 2)},
                    {"date": fmt(r["neck_right"][0]), "price": round(r["neck_right"][1], 2)},
                ],
                "target": {
                    "price": round(r["target"], 2),
                    "from": fmt(r["entry_pos"]),
                    "to": fmt(r["exit_pos"]),
                },
                "head": {"date": fmt(r["head"][0]), "price": round(r["head"][1], 2)},
                "shoulders": [
                    {"date": fmt(s[0]), "price": round(s[1], 2)} for s in r["shoulders"]
                ],
            }
        )
    return out


def open_entry(df: pd.DataFrame, **_):
    """Pas de position ouverte exposée : on ne compte que les figures clôturées."""
    return None


def indicators(df: pd.DataFrame, **_) -> pd.DataFrame:
    """Aucun overlay continu (la ligne de cou est propre à chaque figure)."""
    return pd.DataFrame(index=df.index)
