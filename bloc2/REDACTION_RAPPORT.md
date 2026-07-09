# Brouillon de rédaction — chapitre Bloc 2 (pour intégration LaTeX)

> **À l'attention du chat qui rédige le rapport sur `main`.** Ce fichier est un brouillon
> du chapitre Bloc 2, calé sur le style de `rapport/03_bloc1.tex` (structure *théorie →
> conditions → résultats → limites* par méthode, environnements `conditions`/`limites`,
> chiffres réels). À intégrer dans `rapport/04_bloc2.tex` au moment de la fusion. Les
> **chiffres sont réels**, extraits de `bloc2/03_resultats/`.

---

## Trame du chapitre

**Question du chapitre** : *les signaux d'information exogène (contrats publics, transactions
du Congrès, régulations, résultats) produisent-ils un rendement anormal significatif sur les
titres concernés, ou l'information est-elle déjà intégrée dans les prix ?*

Quatre étapes : étude d'événement → tests par sens → khi-deux → régression de Poisson.

---

## Squelette LaTeX proposé

```latex
\chapter{Bloc 2 --- valeur des signaux d'information}
\label{chap:bloc2}

Ce chapitre mesure la valeur prédictive de l'information \emph{exogène}. À la
différence du Bloc 1 (information contenue dans les prix), on étudie ici des
signaux extérieurs collectés via des agents \texttt{n8n}~: attributions de
contrats fédéraux, transactions déclarées du Congrès, régulations sectorielles,
surprises de résultats. La variable-juge est le \textbf{rendement anormal
cumulé} (\textit{CAR}).

% =====================================================================
\section{Cadre : l'étude d'événement}
\label{sec:b2-cadre}

\subsection{Présentation théorique}
Le \textbf{modèle de marché} estime le rendement normal d'un titre~:
\[ R_{i,t} = \alpha_i + \beta_i R_{m,t} + \varepsilon_{i,t}, \]
$\alpha_i,\beta_i$ étant estimés par MCO sur une \textbf{fenêtre d'estimation}
($J{-}250$ à $J{-}11$). Le \textbf{rendement anormal} sur la fenêtre
d'événement ($J{-}1$ à $J{+}5$) est
\[ AR_{i,t} = R_{i,t} - (\hat\alpha_i + \hat\beta_i R_{m,t}), \qquad
   CAR_i = \sum_{t} AR_{i,t}. \]
Sous l'hypothèse d'efficience semi-forte, $E[CAR]=0$~\cite{fama1970,mackinlay1997}.

\begin{conditions}
Rendement de marché = moyenne S\&P~500 (colonne \texttt{MARCHE} du Bloc~3).
Fenêtre d'estimation d'au moins 60~jours pour un $\beta$ fiable~; événements
hors historique de prix écartés.
\end{conditions}

% =====================================================================
\section{Étape 1 --- le signal déplace-t-il le cours ?}
\subsection{Résultats}
% Chiffres réels : bloc2/03_resultats/etape1_event_study.txt
\begin{table}[H]\centering
\caption{CAR moyen par signal (test bilatéral, Bonferroni $=0{,}025$).}
\begin{tabular}{@{}lrrrc@{}}\toprule
Signal & $n$ & $CAR$ moyen & $p$ (Student) & Verdict \\\midrule
Contrat public & 174  & $+0{,}0027$ & $0{,}35$ & non \\
Régulation     & 2\,030 & $-0{,}0015$ & $0{,}20$ & non \\\bottomrule
\end{tabular}\end{table}
Aucun des deux signaux ne dégage de CAR significatif~: l'information publique
paraît déjà incorporée dans les cours. (Figure~: \texttt{etape1\_car.png}.)

% =====================================================================
\section{Étape 2 --- le sens du signal porte-t-il un edge ?}
\subsection{Présentation théorique}
% Student 1-échantillon + Wilcoxon + Bonferroni (cf. Bloc 1, réutilisés).
\subsection{Résultats}
% bloc2/03_resultats/etape2_tests.txt
\begin{table}[H]\centering
\caption{CAR moyen par (signal, sens). Seuil Bonferroni $=0{,}017$.}
\begin{tabular}{@{}llrrc@{}}\toprule
Signal & Sens & $n$ & $CAR$ moyen & $p$ (Student) \\\midrule
Contrat    & attribution  & 174   & $+0{,}0027$ & $0{,}35$ \\
Régulation & significative & 640  & $-0{,}0047$ & $0{,}02$ \\
Régulation & standard      & 1\,390 & $-0{,}0001$ & $0{,}97$ \\\bottomrule
\end{tabular}\end{table}
Une régulation \emph{significative} entraîne un CAR de $-0{,}47\%$
($p=0{,}02$)~: détectable au seuil de 5\% brut, mais \textbf{rejeté après
Bonferroni}. C'est le signal le plus proche de la significativité.

\begin{limites}
Shapiro rejette la normalité ($p<10^{-10}$)~; validité par le TCL, Wilcoxon
confirme. Une fuite d'information avant $J0$ diluerait l'effet mesuré.
\end{limites}

% =====================================================================
\section{Étape 3 --- le sens est-il lié à l'issue ?}
% khi-deux + V de Cramér (même cadre théorique que Bloc 1 §3)
\subsection{Résultats}
% bloc2/03_resultats/etape3_chi2.txt
Pour les régulations, le sens (\emph{significative}/\emph{standard}) et l'issue
(hausse/baisse du CAR) sont \textbf{indépendants} ($\chi^2=0{,}40$, ddl$=1$,
$p=0{,}53$, $V=0{,}01$). Le test prendra sa pleine valeur avec le signal Congrès
(achat/vente), non encore branché.

% =====================================================================
\section{Étape 4 --- concentration sectorielle (Poisson)}
\subsection{Présentation théorique}
% GLM Poisson : log E[Y] = beta0 + effets secteur ; test de sur-dispersion.
\[ \log \mathbb{E}[Y_i] = \beta_0 + \sum_s \beta_s \mathbb{1}[\text{secteur}_i=s],
   \qquad Y_i \sim \mathcal{P}(\lambda_i). \]
\begin{conditions}
Comptage $Y\ge 0$~; \textbf{équidispersion} (variance $=$ moyenne). En cas de
sur-dispersion, recours à la \textbf{binomiale négative}~\cite{cameron2013}.
\end{conditions}
\subsection{Résultats}
% bloc2/03_resultats/etape4_poisson.txt
Les événements se concentrent significativement (Consumer Disc. $\times1{,}6$,
Energy $\times1{,}6$, IT $\times1{,}3$~; $p<0{,}01$). Mais la
\textbf{sur-dispersion} est massive (ratio variance/moyenne $\approx 27$)~: en
binomiale négative (AIC $506$ vs $1796$), le nombre d'effets significatifs
tombe de \textbf{5 à 2}. « Significatif » n'est pas « robuste ».

% =====================================================================
\section{Contagion --- un signal sur A déplace-t-il d'autres actifs B ?}
\label{sec:b2-contagion}
On ne cherche plus l'effet du signal sur \emph{son} titre, mais sur les actifs
\textbf{liés} à A~: ses \emph{pairs corrélés} (les plus corrélés en rendement,
data-driven) et ses \emph{thèmes / matières premières} (proxies ETF déclarés~:
Tesla~$\to$~lithium, défense~$\to$~ETF ITA\ldots).

\subsection{Impact simultané (étape 5)}
% bloc2/03_resultats/etape5_contagion.txt
Autour du signal sur A, le CAR moyen des cibles est significativement positif~:
pairs corrélés $+0{,}27\%$ ($p\approx0{,}003$), thèmes/matières $+0{,}26\%$
($p\approx6\times10^{-4}$). \textbf{L'écosystème de A réagit.}

\subsection{Impact décalé / lead-lag (étape 6)}
% bloc2/03_resultats/etape6_leadlag.txt
On sépare la réaction \emph{immédiate} ($J0$--$J1$) de la \emph{décalée}
($J2$--$J5$), et on teste (esprit Granger) si $AR_A(J0)$ prédit $AR_B(J{+}1)$.
L'effet est surtout \textbf{synchrone} (immédiat significatif)~; le décalé n'est
pas significatif. Léger entraînement $A\to B$ le lendemain sur les pairs
corrélés (pente $+0{,}03$, $p\approx0{,}05$).

\subsection{Cartographie fine (étape 7)}
% bloc2/03_resultats/etape7_carte_contagion.txt + etape7_heatmap.png
Au niveau du couple $A\to B$, des canaux nets apparaissent~: \texttt{UNH}$\to$
\texttt{HUM} ($+2{,}8\%$), entraînement mutuel des laboratoires pharmaceutiques
(\texttt{JNJ/LLY/PFE}$\to$\texttt{MRK}, $+1{,}6\%$), et un effet de
\emph{substitution} dans la défense (\texttt{BA}$\to$\texttt{RTX}, $-0{,}7\%$~;
\texttt{LMT/BA}$\to$ETF défense en baisse). \emph{[Insérer
\texttt{etape7\_heatmap.png}.]}

% =====================================================================
\section{Synthèse du Bloc 2}
\textbf{Impact direct}~: sur les signaux publics testés (contrats, régulations),
aucun ne dégage d'edge significatif sur son propre titre après correction~: le
marché a anticipé l'information. L'\emph{achat du Congrès} montre le CAR le plus
élevé ($+2{,}0\%$) mais sur un échantillon trop faible ($n=19$) pour conclure.
\textbf{Contagion}~: un signal sur A \emph{déplace} significativement les actifs
liés (pairs, matières premières), surtout de façon synchrone~; la cartographie
fine révèle des canaux interprétables (santé qui s'entraîne, défense en
substitution). Les événements se concentrent par secteur.
```

---

## Références bibliographiques à ajouter dans `biblio.bib`
- `fama1970` — Fama, E. (1970). *Efficient Capital Markets*. Journal of Finance.
- `mackinlay1997` — MacKinlay, A.C. (1997). *Event Studies in Economics and Finance*. JEL.
- `cameron2013` — Cameron & Trivedi (2013). *Regression Analysis of Count Data*.

## Notes pour la fusion
- Les chiffres proviennent de `bloc2/03_resultats/` (relançables). Si la clé FMP est ajoutée
  et que Congrès/earnings sont collectés, **relancer les scripts** régénère les tableaux
  (le nombre de signaux testés change → adapter les seuils Bonferroni affichés).
- La figure `etape1_car.png` est dans `bloc2/03_resultats/` (à copier vers les assets du rapport).
- Ne PAS mettre le code complet dans le rapport (consigne M1) : seules les lignes-clés /
  formules, le reste en annexe.
