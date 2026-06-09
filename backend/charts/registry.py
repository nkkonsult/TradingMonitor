"""Registre central des stratégies : source UNIQUE de vérité.

Utilisé à la fois par le dashboard (app/analysis.py) et par le scan batch offline
(charts/scan.py) -> garantit que les mêmes définitions/params produisent les mêmes
trades partout. Chaque entrée = (module, libellé, params propres à la variante).

`PARAMS_VERSION` versionne l'ensemble des réglages : toute ligne de la base de
détections porte cette version -> reproductibilité (on sait quels seuils l'ont produite).
"""
from __future__ import annotations

from .strategy import head_shoulders, ma_crossover, rsi

STRATEGIES = {
    "ma_crossover": (ma_crossover, "Croisement de moyennes mobiles", {}),
    "rsi_classic": (rsi, "RSI 30/70", {"lower": 30, "upper": 70}),
    "rsi_strict": (rsi, "RSI 20/80 (strict)", {"lower": 20, "upper": 80}),
    "rsi_trend": (rsi, "RSI 30/70 + filtre MM200", {"lower": 30, "upper": 70, "trend_ma": 200}),
    "hs_inverse": (head_shoulders, "Épaule-tête-épaule inversé (achat)", {"direction": "bullish"}),
    "hs_classic": (head_shoulders, "Épaule-tête-épaule (vente/short)", {"direction": "bearish"}),
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
}
