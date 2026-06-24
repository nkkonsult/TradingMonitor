---
name: 10-series-temporelles
description: Synthèse cours "Séries temporelles S2" (Davide Giraudo, M1 DUAS/Stat Strasbourg, 30 pages) — cadre théorique L², processus stationnaires, MA/AR/ARMA/ARIMA, estimation Yule-Walker, prédiction linéaire, AIC, tests stationnarité
metadata:
  type: reference
---

# Séries temporelles S2 (Davide Giraudo, M1 DUAS/Stat Strasbourg, 30 pages)

> Cours **très théorique** (bien plus rigoureux qu'un cours pratique standard) — cadre Hilbertien L², projection orthogonale, opérateur de retard B, équations de récurrence.

## 1. Cadre général

### Définitions de base
- Série temporelle : (xₜ)ₜ=1..T = réalisation d'un processus stochastique (Xₜ)
- On suppose **temps discret** (t ∈ ℤ)
- Modèle de base : Xₜ = f(t, εₜ) — trop général
- **Modèle additif de période p** :
$$ X_t = T(t) + S(t; p) + \varepsilon_t $$
avec T(·) tendance et S(·; p) périodique de période p.

### Définitions importantes
- **Coefficients saisonniers** : Sᵢ^(p) = S(i; p), avec Σ Sᵢ^(p) = 0
- **Modèle de Buys-Ballot** : Xₜ = β₀ + β₁t + S_{j(t,p)}^(p) + εₜ
- **Modèle multiplicatif** : Xₜ = T(t) × S(t; p) × (1 + εₜ)

## 2. Partie déterministe — lissage

### 2.1 Moyenne mobile
- **Opérateur de retard** : B((xₜ)) = (xₜ₋₁)
- **Opérateur avance** : F = B⁻¹
- **Moyenne mobile d'ordres (m₋, m₊)** :
$$ M_{(m_-, m_+, \theta)} = \sum_{i=-m_-}^{m_+} \theta_i B^{-i} $$
- **Centrée** si m₋ = m₊ = m
- **Symétrique** si centrée et θ₋ᵢ = θᵢ
- **Polynôme caractéristique** : P(z, θ) = Σ θ₋ᵢ₋ₘ zⁱ

### 2.2 Moyenne mobile arithmétique M_p^(A)
Cas pair (p) :
$$ \theta_p^{(A)} = \left(\frac{1}{2p}, \frac{1}{p}, \ldots, \frac{1}{p}, \frac{1}{2p}\right) $$
Cas impair (p) : θ = (1/p, …, 1/p)

### 2.3 Estimation tendance + saisonnière (3 étapes)
1. **Choix de la moyenne mobile M** telle que MT(t) = T(t) (tendance conservée) ET MS(t; p) = 0 (saisonnalité supprimée)
2. **Estimation des coefficients saisonniers** : S̃_k^(p) = moyenne des résidus puis recentrage Σ = 0
3. **Estimation de la tendance** par moindres carrés sur série corrigée des variations saisonnières (CVS) :
$$ x_t^{CVS} = x_t - \widehat{S}_{j(t,p)}^{(p)} $$
$$ \widehat{\beta} = \arg\min \sum_t (x_t^{CVS} - g(t, \beta))^2 $$

**Prédiction** à horizon h :
$$ \widehat{x}_{T+h} = \widehat{T}(T+h) + \widehat{S}_{j(T+h, p)}^{(p)} $$

### 2.4 Lissage exponentiel
- **LES** (Lissage Exponentiel Simple) :
$$ x_{T+1}^{LES}(\gamma) = (1-\gamma) \sum_{k=0}^\infty \gamma^k x_{T-k} $$
- **LED** (Lissage Exponentiel Double) : prédiction de la forme aₜ·h + bₜ, capable de capturer une tendance

## 3. Processus stochastiques L² — cadre théorique

### 3.1 Espace L²
- L²(Ω, 𝓕, ℙ) = espace des variables aléatoires telles que 𝔼[X²] < ∞
- **Produit scalaire** : ⟨X, Y⟩ = 𝔼[XY]
- **Norme** : ‖X‖₂ = √𝔼[X²]
- **Cauchy-Schwarz** : (𝔼[XY])² ≤ 𝔼[X²]·𝔼[Y²]
- **L² est un espace de Hilbert** ⇒ théorème de projection orthogonale disponible
- Orthogonalité : ⟨X, Y⟩ = 0 ⇔ 𝔼[XY] = 0

### 3.2 Définitions clés
- **Processus stochastique** : famille (Xₜ)ₜ∈E de variables aléatoires
- **Temps discret** si E dénombrable, continu sinon
- **Ergodicité en moyenne quadratique** : la moyenne temporelle converge vers 𝔼[X₀]

### 3.3 Bruit blanc
- **Bruit blanc FORT** : (ηₜ) **indépendantes**, 𝔼[ηₜ] = 0, 𝔼[ηₜ²] = σ²
- **Bruit blanc FAIBLE** : 𝔼[ηₜ] = 0, 𝔼[ηₜ²] = σ², Cov(ηₛ, ηₜ) = 0 pour s ≠ t
- Dans le cours, « bruit blanc » = bruit blanc faible (par défaut)

### 3.4 Stationnarité
- **Stationnaire au second ordre** : 𝔼[Xₜ²] < ∞, 𝔼[Xₜ] = 𝔼[X₀], et :
$$ \text{Cov}(X_t, X_{t+h}) = \text{Cov}(X_0, X_h) =: \gamma(h) $$
- γ(h) = **fonction d'auto-covariance**
- **Stationnaire au sens strict** : (Xₜ₊₁, …, Xₜ₊ₕ) et (X₁, …, Xₕ) ont même loi
- **Processus gaussien** : toute combinaison linéaire suit une loi normale
- **Mouvement brownien** : B₀=0, B_t−B_s ~ 𝒩(0, t−s), incréments indépendants
- **Marche aléatoire** : Xₜ = Σ εₜ, **PAS stationnaire** (sauf σ=0)

### 3.5 Auto-corrélation
$$ \rho(h) = \frac{\gamma(h)}{\gamma(0)} = \frac{\text{Cov}(X_t, X_{t+h})}{\sigma^2} $$

### 3.6 Auto-corrélation **PARTIELLE** (PACF) ⭐
$$ \tau(h) = \frac{\text{Cov}(U_h, V_h)}{(\text{Var}(U_h)\text{Var}(V_h))^{1/2}} $$
où Uₕ et Vₕ sont les résidus après projection sur l'information intermédiaire.

➡️ τ(h) mesure la **dépendance directe** entre Xₜ et Xₜ₊ₕ, après avoir retiré l'effet des instants intermédiaires.

## 4. Espérance linéaire et innovation

### Espérance linéaire 𝔼ℒ(Y | (Xᵢ))
- **Projection orthogonale** de Y sur vect{Xᵢ, i ∈ I}
- ≠ espérance conditionnelle 𝔼[Y | X] (sauf cas gaussien centré où elles coïncident)
- Pour Y, X centrés : 𝔼ℒ(Y | 1, X) = 𝔼ℒ(Y | X)

### Histoire et innovation
- **Histoire** : 𝓗ₜ^X = vect{Xₛ, s ≤ t}
- **Innovation** :
$$ \varepsilon_t = X_t - \mathbb{EL}(X_t | \mathcal{H}_{t-1}^X) $$
⇒ Ce qui est "nouveau" à l'instant t après avoir connu tout le passé.

## 5. Équation de récurrence P(B)Xₜ = Yₜ

### Proposition 3.36 — Existence/unicité
Si P(z) ≠ 0 sur le **cercle unité** (|z| = 1), alors P(B) est inversible et il existe une famille (aⱼ) absolument sommable telle que :
$$ (P(B))^{-1} = \sum_j a_j B^j $$

### Proposition 3.37 — Cas important pour AR
Si Yₜ a moments d'ordre 1 bornés :
1. **Inversible** : P n'a aucune racine sur cercle unité → Xₜ = Σⱼ aⱼ Yₜ₋ⱼ (somme bilatérale)
2. **Causal** : P n'a aucune racine dans le **disque unité fermé** → Xₜ = Σⱼ₌₀^∞ aⱼ Yₜ₋ⱼ (dépend uniquement du passé) ⭐

## 6. Processus MA(q) — Moyenne Mobile

### Définition
$$ X_t = Q(B) \eta_t = \eta_t - \sum_{k=1}^q \theta_k \eta_{t-k} $$
où Q(z) = 1 − Σ θₖ zᵏ et (ηₜ) bruit blanc faible.

### Propriétés clés
- ✅ **Toujours stationnaire** au second ordre (pas d'hypothèse supplémentaire)
- 𝔼[Xₜ] = 0
- Auto-covariance : γ(h) = 𝔼[η₀²] · Σ θᵢθᵢ₊ₕ pour 0 ≤ h ≤ q, et **γ(h) = 0 pour h > q** ⭐

### Forme canonique
Si Q n'a aucune racine de module 1, ∃ Q̃ avec toutes racines de module > 1 tel que Xₜ = Q̃(B)εₜ.

### Estimation
- Tester si ρ(h) ≈ 0 pour h > q via **intervalle de confiance** asymptotique sur ρ̂ₜ(h)
- Si ρ̂ₜ(h) ∈ Î_q,α pour tout h > q → accepter MA(q)
- Sinon recommencer avec q+1
- En pratique, h > 20 suffit
- Coefficients estimés via **algorithme des innovations**

## 7. Processus AR(p) — Auto-Régressif ⭐⭐

### Définition
$$ P(B) X_t = X_t - \sum_{k=1}^p \Phi_k X_{t-k} = \eta_t $$

### Existence/unicité (Proposition 5.1)
- **Inversible** si P n'a pas de racine sur cercle unité : Xₜ = Σ aᵢ ηₜ₋ᵢ (bilatéral)
- **Causal** si P n'a pas de racine dans disque unité fermé : Xₜ = Σᵢ₌₀^∞ aᵢ ηₜ₋ᵢ

### Forme canonique
P̃(B)Xₜ = εₜ avec P̃ ayant toutes racines de module > 1.

### Caractérisation par PACF ⭐
Si Xₜ ~ AR(p) :
$$ \tau(p) = \Phi_p \quad \text{et} \quad \tau(h) = 0 \text{ pour } h > p $$

➡️ **Le PACF "coupe" après le décalage p** — c'est LE test visuel pour identifier un AR.

### Équations de Yule-Walker (Proposition 5.5)
$$ \mathbb{E}[\eta_0^2] = \gamma(0) - \sum_{i=1}^p \Phi_i \gamma(i) $$
$$ (\rho(1), \ldots, \rho(h))^\top = \Gamma_h \cdot (\Phi_1, \ldots, \Phi_h)^\top $$

⇒ permet d'**estimer** les Φᵢ par inversion : Φ̂ = Γ̂_h⁻¹ ρ̂.

### Estimation de l'ordre p
$$ \widehat{p} = \inf\{r \geq 1, \forall h \geq r, |\widehat{\Phi}_h| \leq Q_{\mathcal{N}}(1 - \alpha/2)/\sqrt{T}\} $$
Test par quantile normale, en pratique α = 0.05.

### Prédiction (Proposition 5.7)
**Récursivement** :
$$ \widehat{X}_{T+1} = \sum_{i=1}^p \widehat{\Phi}_i X_{T+1-i} $$
$$ \widehat{X}_{T+2} = \widehat{\Phi}_1 \widehat{X}_{T+1} + \sum_{i=2}^p \widehat{\Phi}_i X_{T+2-i} $$

Et résidus :
$$ \widehat{\eta}_t = X_t - \sum_{i=1}^p \widehat{\Phi}_i X_{t-i} $$

## 8. Processus ARMA(p, q)

### Définition
$$ P(B) X_t = Q(B) \eta_t $$
- ARMA(p, 0) = AR(p)
- ARMA(0, q) = MA(q)
- ARMA(0, 0) = bruit blanc faible

### Représentation minimale
P et Q **sans racines communes** (sinon on les élimine).

### Représentation MA(∞) ou AR(∞)
- Si P sans racines sur disque unité : Xₜ = Σᵢ₌₀^∞ Φᵢ* ηₜ₋ᵢ (causal MA infini)
- Si Q sans racines sur disque unité : ηₜ = Σᵢ₌₀^∞ θᵢ* Xₜ₋ᵢ (inversible AR infini)

### Estimation ARMA — méthode complète (Section 6.5) ⭐⭐
**7 étapes** :

0. **Test de stationnarité** :
   - **KPSS** (Kwiatkowski-Phillips-Schmidt-Shin)
   - **Dickey-Fuller** (test de racine de module 1 dans AR)
1. **Centrage** : Xₜ ← Xₜ − μ̂ₜ
2. Estimer **ACF** et **PACF**
   - Si décroissance trop lente → transformation **Box-Cox** : g_λ(X) = (Xλ−1)/λ
3. **Estimation des ordres p et q** :
   - p_max via PACF (idem AR)
   - q_max via intervalle de confiance sur ρ (idem MA)
4. Pour chaque (p, q), estimer (Φ, θ) **via algorithme des innovations**
5. **Critère AIC** :
$$ \text{AIC}_{p,q} = 2\left(\ln \widehat{\sigma}_{p,q} + \frac{p+q}{T}\right) $$
   → on prend (p, q) minimisant AIC
6. **Prédiction** récursive (formule complexe combinant AR et MA infinis)
7. **Validation** : test de Box-Pierce sur les résidus standardisés
   - H₀ : « ηₜ est un bruit blanc fort »
   - Statistique : S_BP(H) = T · Σ ρ̂²_η(h)
   - ~ χ²(H − p − q) sous H₀
   - Rejet si S_BP > χ²₁₋α(H − p − q)
   - En pratique 15 ≤ H ≤ 20

## 9. Processus ARIMA(p, d, q) ⭐

### Définition 7.1
(Xₜ) est ARIMA(p, d, q) si le **processus différencié** :
$$ Y_t = (I - B)^d X_t $$
est un ARMA(p, q).

Forme générale :
$$ P(B)(I - B)^d X_t = Q(B) X_t $$

### Pourquoi ?
**Différencier d fois rend le processus stationnaire** :
- Marche aléatoire (non stationnaire) : Xₜ = Xₜ₋₁ + ηₜ ⇒ (I−B)Xₜ = ηₜ = bruit blanc ⇒ ARIMA(0, 1, 0) ⭐
- Tendance polynomiale d'ordre d−1 + bruit ⇒ ARIMA(0, d, d)

### Note importante
- Le processus n'est **pas défini de manière unique** (à constante près)

---

## 🎯 Applications au projet TradingMonitor

### Pertinence directe pour le Bloc 3 (déjà partiellement implémenté)

L'ARIMA a déjà été utilisé sur les indices sectoriels du Bloc 3. Avec ce cours rigoureux, on peut **professionnaliser** le protocole :

#### Pipeline ARIMA complet à appliquer
1. ✅ **Test de stationnarité KPSS + Dickey-Fuller** sur chaque série
2. ✅ Si non stationnaire → différencier (d = 1 ou 2)
3. ✅ Tracer **ACF** + **PACF** pour identifier p, q candidats
4. ✅ Sélectionner (p, q) par **AIC minimal** sur grille
5. ✅ Estimer les coefficients via Yule-Walker (AR) ou algorithme des innovations (ARMA)
6. ✅ **Test de Box-Pierce sur résidus** pour valider H₀ : bruit blanc

➡️ Ce protocole en 7 étapes est **directement issu du cours** et donne une légitimité méthodologique forte au rapport.

### Marche aléatoire = ARIMA(0,1,0) ⭐
**Très important pour le projet** : un cours d'actions est typiquement une marche aléatoire (en log-prix). Donc :
- Log-prix → ARIMA(0, 1, 0) au minimum
- Différencier → on retombe sur les **rendements** ηₜ
- ⇒ Les rendements logarithmiques sont (à peu près) un bruit blanc → c'est l'**hypothèse de marché efficient** (EMH)
- Toute déviation de cette hypothèse = opportunité d'arbitrage (= le but du projet)

### Stationnarité ⚠️
**Erreur classique en finance** : utiliser les prix bruts au lieu des rendements. Les prix sont NON stationnaires → l'autocorrélation calculée n'a pas de sens. **Toujours travailler sur les rendements** (différentiation log).

### Innovation vs ε standard
Le cours distingue rigoureusement :
- εₜ = erreur du modèle (peut être MA d'autres innovations)
- ηₜ = bruit blanc d'innovation = vraie nouveauté

Important pour les modèles GARCH (où l'innovation a une variance variable).

### Cadre L² et projection orthogonale
- La **prédiction linéaire optimale** = projection sur le passé
- Cadre purement géométrique ⇒ pas besoin d'hypothèses gaussiennes
- ⚠️ Pour des prévisions plus précises, on peut utiliser l'**espérance conditionnelle** (gaussien centré) mais elle est plus dure à calculer

### PACF comme outil de sélection AR
Application directe : pour identifier l'ordre d'un AR sur un indice :
- Tracer PACF
- Trouver le décalage p après lequel τ(h) "coupe" (< 1.96/√T)
- ⇒ ordre AR identifié visuellement

### Limites pour le projet
- Le cours **ne couvre pas** :
  - **SARIMA** (saisonnalité multiplicative) — extension naturelle
  - **GARCH** (variance variable) — pertinent en finance pour volatilité
  - **Causalité de Granger** — utile pour tester si une série en prédit une autre (Bloc 3 !)
  - **VAR** (vecteur autorégressif, multi-séries) — utile pour modéliser plusieurs indices ensemble

---

## ✅ Méthodes acquises dans ce cours
- Modèles additif / multiplicatif / Buys-Ballot
- Moyenne mobile (centrée, symétrique, polynôme caractéristique)
- Lissage exponentiel simple (LES) et double (LED)
- Cadre L², projection orthogonale
- Bruit blanc fort / faible
- Stationnarité au second ordre / stricte
- Auto-covariance γ(h), auto-corrélation ρ(h)
- **Auto-corrélation PARTIELLE τ(h) — PACF** ⭐
- Espérance linéaire 𝔼ℒ
- Innovation
- Opérateur de retard B, équations de récurrence P(B)Xₜ = Yₜ
- Causalité, inversibilité
- **MA(q)** (caractérisation par γ(h) = 0, h > q)
- **AR(p)** (caractérisation par PACF, équations Yule-Walker)
- **ARMA(p, q)** + pipeline 7 étapes
- **ARIMA(p, d, q)** — différenciation pour stationnariser
- Tests KPSS, Dickey-Fuller
- AIC pour sélection (p, q)
- **Box-Pierce** pour validation résidus
- Algorithme des innovations
- Transformation Box-Cox

## 🆕 À étudier (PAS dans ce cours)
- **SARIMA** (saisonnalité explicite)
- **GARCH / ARCH** (volatilité variable) — essentiel en finance
- **VAR** (multi-séries) — utile pour Bloc 3
- **Causalité de Granger** — pour tester relations inter-actions
- **Test de Ljung-Box** (amélioration de Box-Pierce)
- **Cointégration** (relations long-terme entre séries non stationnaires)
- **TimeSeriesSplit** sklearn (cf [[05-apprentissage-introduction]])
- **Walk-forward backtesting**
