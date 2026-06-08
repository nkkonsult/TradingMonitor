"""charts — moteur d'analyse de graphiques (détection de stratégies + backtest + stats).

Conçu pour le Pilier A (analyse technique) du Trading Agent. Découpage clé :
chaque stratégie produit une liste de Trade ; backtest/stats/render sont
indépendants de la stratégie. Brancher une nouvelle stratégie (ex. épaule-tête-épaule)
= écrire un nouveau module dans strategy/, sans toucher au reste.
"""
