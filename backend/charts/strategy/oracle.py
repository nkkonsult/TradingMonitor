"""Stratégie ORACLE — le TÉMOIN POSITIF du protocole de validation (mémoire).

Toutes les autres stratégies ne décident qu'avec de l'information PASSÉE. L'oracle,
lui, TRICHE : à chaque date candidate il regarde le rendement des `horizon` jours
SUIVANTS (information future, interdite en réalité) et n'entre que si ce rendement
dépasse `seuil`. Son edge est donc réel et fort par construction.

But : un outil de validation peut échouer de deux façons — laisser passer un faux
signal (faux positif) OU rejeter un vrai signal (faux négatif). Les dix vraies
stratégies testent le premier risque ; l'oracle teste le second. S'il franchit
toutes les portes du protocole, c'est la preuve que l'outil sait aussi dire « oui ».

Choix de conception (discutés dans le rapport) :
  - oracle BRUITÉ, pas parfait : il ne vise pas le minimum absolu, il entre dès que
    l'avenir proche est positif -> edge réel mais pas caricatural ;
  - SEUIL MODESTE (v2) : avec un seuil de +25 %, le témoin ne tradait que les
    rebonds extrêmes (2009, 2020) -> edge écrasant (t ~ 120) ET autocorrélation
    mensuelle de régime. Un tel témoin sort du domaine des outils qu'il doit
    calibrer (Dickey-Fuller sans puissance sur une série trop tassée). Un seuil
    de +5 % répartit les entrées sur tous les régimes : le témoin ressemble à
    une stratégie réaliste tout en gardant un avantage franchement positif ;
  - VOLUME MAÎTRISÉ : un espacement minimal `cooldown` entre deux entrées empêche
    l'oracle de trader tous les jours et le maintient dans le même ordre de grandeur
    que les vraies stratégies, sinon il écraserait les comparaisons du chapitre
    « contexte » (ANOVA, khi-deux).

Même contrat que les autres stratégies : detect_trades(df, ...) -> list[Trade].
"""
from __future__ import annotations

import pandas as pd

from ..trade import Trade

# Paramètres calibrés (sur 40 titres) pour ~2 000 trades au total, soit le même
# ordre de grandeur que les vraies stratégies (rsi_strict ~1 000, rsi_trend ~2 800) :
# un oracle qui trade des dizaines de milliers de fois écraserait les comparaisons.
HORIZON = 30     # nb de jours de bourse « vus » dans le futur (la triche)
SEUIL = 0.05     # on n'entre que si le futur proche rapporte au moins +5 % (v2, cf. ci-dessus)
COOLDOWN = 250   # ~1 an de bourse de repos entre deux entrées (bride le volume)


def detect_trades(
    df: pd.DataFrame,
    *,
    horizon: int = HORIZON,
    seuil: float = SEUIL,
    cooldown: int = COOLDOWN,
    **_,
) -> list[Trade]:
    """Trades « clairvoyants » : entrée quand les `horizon` jours suivants montent
    d'au moins `seuil`, sortie `horizon` jours plus tard, espacés de `cooldown`."""
    close = df["Close"]
    n = len(close)
    if n <= horizon + 1:
        return []

    prices = close.to_numpy()
    dates = df.index
    trades: list[Trade] = []
    i = 0
    while i < n - horizon:
        futur = prices[i + horizon] / prices[i] - 1.0  # rendement futur (triche)
        if futur >= seuil:
            trades.append(
                Trade(
                    entry_date=dates[i],
                    entry_price=float(prices[i]),
                    exit_date=dates[i + horizon],
                    exit_price=float(prices[i + horizon]),
                    direction=1,
                )
            )
            i += horizon + cooldown  # on saute la position + le délai de repos
        else:
            i += 1
    return trades
