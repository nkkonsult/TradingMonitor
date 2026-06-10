"""Registre central des stratégies : source UNIQUE de vérité.

Utilisé à la fois par le dashboard (app/analysis.py) et par le scan batch offline
(charts/scan.py) -> garantit que les mêmes définitions/params produisent les mêmes
trades partout. Chaque entrée = (module, libellé, params propres à la variante).

`PARAMS_VERSION` versionne l'ensemble des réglages : toute ligne de la base de
détections porte cette version -> reproductibilité (on sait quels seuils l'ont produite).
"""
from __future__ import annotations

from .strategy import double_top_bottom, head_shoulders, ma_crossover, rsi, support_resistance

STRATEGIES = {
    "ma_crossover": (ma_crossover, "Croisement de moyennes mobiles", {}),
    "rsi_classic": (rsi, "RSI 30/70", {"lower": 30, "upper": 70}),
    "rsi_strict": (rsi, "RSI 20/80 (strict)", {"lower": 20, "upper": 80}),
    "rsi_trend": (rsi, "RSI 30/70 + filtre MM200", {"lower": 30, "upper": 70, "trend_ma": 200}),
    "hs_inverse": (head_shoulders, "Épaule-tête-épaule inversé (achat)", {"direction": "bullish"}),
    "hs_classic": (head_shoulders, "Épaule-tête-épaule (vente/short)", {"direction": "bearish"}),
    "db_bottom": (double_top_bottom, "Double creux (achat)", {"direction": "bottom"}),
    "dt_top": (double_top_bottom, "Double sommet (vente/short)", {"direction": "top"}),
    "sr_breakout": (support_resistance, "Cassure de résistance → hausse (achat)", {"variant": "breakout"}),
    "sr_breakdown": (support_resistance, "Cassure de support → baisse (short)", {"variant": "breakdown"}),
}

PARAMS_VERSION = "v1"

# Mode d'évaluation de chaque stratégie -> détermine le graphe de comparaison pertinent :
#  - "overlay" : signal de SORTIE (éviter une chute) -> comparer au buy & hold (tenir).
#  - "entry"   : signal d'ENTRÉE (détecter une montée) -> comparer au HASARD (pile ou face).
EVAL_MODE = {
    "ma_crossover": "overlay",
    "rsi_classic": "overlay",
    "rsi_strict": "overlay",
    "rsi_trend": "overlay",
    "hs_inverse": "entry",
    "hs_classic": "overlay",
    "db_bottom": "entry",
    "dt_top": "overlay",
    "sr_breakout": "entry",
    "sr_breakdown": "entry",
}
