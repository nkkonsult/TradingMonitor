"""Le contrat commun à toutes les stratégies : un Trade.

C'est la couture centrale du projet. Quelle que soit la stratégie (croisement de
MM, épaule-tête-épaule...), elle produit une liste de Trade. backtest/stats/render
ne connaissent que ce type, donc ils sont réutilisables tels quels.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class Trade:
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: pd.Timestamp
    exit_price: float
    direction: int = 1  # 1 = long (on a acheté), -1 = short (vente à découvert)

    @property
    def return_pct(self) -> float:
        """Rendement du trade (ex. 0.05 = +5%)."""
        return self.direction * (self.exit_price / self.entry_price - 1.0)

    @property
    def holding_days(self) -> int:
        """Durée de détention en jours calendaires."""
        return int((self.exit_date - self.entry_date).days)
