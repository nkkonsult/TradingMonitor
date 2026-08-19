"""ETAPE 1d — La porte 'mois' fermee... vraiment ? Pipeline series temporelles.

PROBLEME : l'etape 1c agrege les edges par mois (1 mois = 1 vote) puis fait un
Student sur les ~190 moyennes mensuelles. Ce test suppose les MOIS independants.
Or des trades durent plusieurs mois (holding jusqu'a ~300 jours) -> deux mois
voisins partagent des trades -> la serie mensuelle est AUTOCORRELEE -> la
variance de la moyenne est encore sous-estimee.

DEMARCHE (pipeline du cours de series temporelles, section estimation ARMA) :
 -1) PRE-TEST D'INDEPENDANCE : Box-Pierce sur la serie mensuelle BRUTE
     (H0 : mois independants / bruit blanc, H = P_MAX retards). Si H0 n'est
     pas rejetee, la condition du test 1c (mois independants) est remplie
     telle quelle : le verdict de 1c tient, aucun modele AR n'est requis et
     la stationnarite n'a pas a etre exigee. On ne corrige que ce qui est
     mesure. Sinon, l'autocorrelation est reelle -> etapes 0 a 6.
  0) STATIONNARITE : tests de Dickey-Fuller (H0 : racine unite) et KPSS
     (H0 : stationnaire) sur la serie mensuelle de chaque strategie.
     Conditions du Student corrige : la serie doit etre stationnaire.
     REGLE DE CONCORDANCE (les H0 sont opposees, "ne pas rejeter" n'est
     jamais une preuve) :
       - DF rejette ET KPSS ne rejette pas -> stationnaire, on corrige ;
       - DF ne rejette pas ET KPSS rejette -> non stationnaire averee,
         la strategie SORT (verdict 'NS') ;
       - autre combinaison -> diagnostic NON CONCLUANT, la strategie SORT
         (verdict '?') : elle n'est ni validee ni rejetee, l'examen revient
         a l'humain (manque de puissance ? serie atypique ?).
  1) CENTRAGE : on travaille sur x_t - x_bar.
  2) ACF / PACF : autocorrelation rho(h) et autocorrelation partielle tau(h).
  3) ORDRE p : le PACF d'un AR(p) 'coupe' apres p -> p_hat = dernier retard
     h <= 6 tel que |tau_hat(h)| > q_N(0.975)/sqrt(T).
  4) AR(p) PAR YULE-WALKER : Phi_hat = Gamma_hat^-1 rho_hat, sigma2_eta par
     l'equation de Yule-Walker d'ordre 0.
  5) VARIANCE CORRIGEE DE LA MOYENNE : pour un AR(p) stationnaire, la variance
     de long terme est gamma_lr = sigma2_eta / (1 - somme Phi_i)^2 et
     Var(x_bar) ~ gamma_lr / T. On en tire un DEFF temporel = gamma_lr/gamma(0),
     T_eff = T/DEFF, et le Student corrige (H0 : mu = 0, H1 : mu > 0),
     seuil de Bonferroni 0.05/11 (le meme que 1b/1c).
  6) VALIDATION : test de Box-Pierce sur les residus de l'AR
     (H0 : les residus sont un bruit blanc), S_BP ~ khi2(H - p), H = 15.

LIMITE ASSUMEE : les mois sans trade (couverture < 100 %) sont traites comme
consecutifs dans la serie ; approximation negligeable quand la couverture est
proche de 100 %, a signaler pour rsi_strict (~70 %).

Entree :  bloc1/01_donnees/trades.csv
Sortie :  bloc1/03_resultats/etape1d_serie_mensuelle.txt
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st
from statsmodels.regression.linear_model import yule_walker
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import adfuller, kpss, pacf

CSV = Path(__file__).resolve().parents[1] / "01_donnees" / "trades.csv"
OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape1d_serie_mensuelle.txt"
ALPHA = 0.05
P_MAX = 6      # ordre AR maximal envisage
H_BP = 15      # nb de retards du test de Box-Pierce (cours : 15 <= H <= 20)
T_MIN = 30     # nb de mois minimal pour invoquer le TCL sur la moyenne mensuelle


def choisir_ordre(x: np.ndarray) -> tuple[int, np.ndarray]:
    """Ordre AR par coupure du PACF : dernier h <= P_MAX hors de la bande.

    Renvoie (p_hat, tau_hat[1..P_MAX]).
    """
    t = len(x)
    tau = pacf(x, nlags=P_MAX, method="ywm")[1:]  # tau(1)..tau(P_MAX)
    bande = st.norm.ppf(1 - ALPHA / 2) / np.sqrt(t)
    signif = [h + 1 for h, v in enumerate(tau) if abs(v) > bande]
    return (max(signif) if signif else 0), tau


def main() -> None:
    df = pd.read_csv(CSV).dropna(subset=["edge"])
    df["mois"] = pd.to_datetime(df["entry_date"]).dt.to_period("M")
    strategies = sorted(df["strategy"].unique())
    seuil = ALPHA / len(strategies)
    lines: list[str] = []
    alertes_par_strat: dict[str, list[str]] = {}

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 132)
    out("ETAPE 1d - SERIE MENSUELLE DES EDGES : la porte 'mois' corrigee de l'autocorrelation")
    out("Entree: trades.csv (%d trades)   Seuil Bonferroni: %.4f   Pipeline: independance ? -> [DF/KPSS -> PACF -> AR(p) Yule-Walker -> Box-Pierce]" %
        (len(df), seuil))
    out("=" * 132)
    out("%-14s %4s %5s | %7s | %5s | %7s %7s | %6s %2s %7s | %6s %6s | %8s %8s %10s | %7s | %7s" %
        ("strategie", "T", "couv%", "p_indep", "br", "p_DF", "p_KPSS", "rho1", "p", "somPhi",
         "DEFF_t", "T_eff", "t_naif", "t_corr", "p_corr", "p_BP", "verdict"))
    out("-" * 148)

    for kname in strategies:
        sub = df[df["strategy"] == kname]
        serie = sub.groupby("mois")["edge"].mean().sort_index()
        x = serie.to_numpy()
        t_len = len(x)
        span = (serie.index[-1] - serie.index[0]).n + 1
        couv = 100.0 * t_len / span

        # --- -1) pre-test : les mois sont-ils independants ? ---------------
        lb_pre = acorr_ljungbox(x, lags=[P_MAX], boxpierce=True)
        p_indep = float(lb_pre["bp_pvalue"].iloc[0])

        # --- 0) stationnarite : Dickey-Fuller (H0 racine unite) + KPSS -----
        # (calcules pour toutes les strategies, a titre informatif ; ils ne
        #  conditionnent le verdict que dans la branche AR)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            p_df = float(adfuller(x, autolag="AIC")[1])
            p_kpss = float(kpss(x, regression="c", nlags="auto")[1])  # borne [0.01, 0.1]

        # --- 1) centrage + 2) ACF/PACF + 3) ordre p ------------------------
        xc = x - x.mean()
        rho1 = float(np.corrcoef(xc[:-1], xc[1:])[0, 1])
        s = x.std(ddof=1)
        t_naif = x.mean() / (s / np.sqrt(t_len))

        alertes: list[str] = []
        if t_len < T_MIN:
            alertes.append("T=%d < %d mois : TCL non invocable sur la moyenne mensuelle" % (t_len, T_MIN))

        if p_indep > ALPHA:
            # === BRANCHE INDEPENDANCE : la condition de 1c est remplie ======
            branche = "indep"
            p_hat, som_phi, deff_t, t_eff = 0, 0.0, 1.0, float(t_len)
            t_corr = t_naif
            p_corr = float(st.t.sf(t_corr, df=t_len - 1))
            p_bp = p_indep  # le pre-test EST le Box-Pierce de cette branche
        else:
            # === BRANCHE AR : autocorrelation reelle -> correction ==========
            branche = "AR"
            p_hat, _ = choisir_ordre(x)

            # --- 4) AR(p) par Yule-Walker + 5) variance de long terme ------
            gamma0 = float(np.var(x))  # estimateur biaise, comme Yule-Walker 'mle'
            if p_hat > 0:
                phi, sigma_eta = yule_walker(x, order=p_hat, method="mle")
                som_phi = float(phi.sum())
                gamma_lr = float(sigma_eta**2) / (1.0 - som_phi) ** 2
                resid = xc[p_hat:] - sum(phi[i] * xc[p_hat - 1 - i:-1 - i] for i in range(p_hat))
            else:
                som_phi = 0.0
                gamma_lr = gamma0
                resid = xc
            deff_t = max(1.0, gamma_lr / gamma0)
            t_eff = t_len / deff_t

            # --- Student corrige : H0 mu = 0, H1 mu > 0 --------------------
            se_corr = np.sqrt(gamma_lr / t_len)
            t_corr = x.mean() / se_corr
            p_corr = float(st.t.sf(t_corr, df=max(2.0, t_eff - 1)))

            # --- 6) validation : Box-Pierce sur les residus ----------------
            bp = acorr_ljungbox(resid, lags=[H_BP], boxpierce=True, model_df=p_hat)
            p_bp = float(bp["bp_pvalue"].iloc[0])

            # --- regle de concordance DF/KPSS ------------------------------
            df_stat = p_df < ALPHA      # DF rejette la racine unite
            kpss_stat = p_kpss > ALPHA  # KPSS ne rejette pas la stationnarite
            if df_stat and not kpss_stat:
                alertes.append("non stationnaire ? DF rejette mais KPSS aussi (p_DF=%.3f, p_KPSS=%.3f) : divergence" % (p_df, p_kpss))
                branche = "?"
            elif (not df_stat) and kpss_stat:
                alertes.append("stationnarite non concluante : DF ne rejette pas (p=%.3f), KPSS conclut stationnaire (p=%.3f)" % (p_df, p_kpss))
                branche = "?"
            elif (not df_stat) and (not kpss_stat):
                alertes.append("serie NON STATIONNAIRE (DF et KPSS concordent : p_DF=%.3f, p_KPSS=%.3f)" % (p_df, p_kpss))
                branche = "NS"
            if p_bp < ALPHA:
                alertes.append("Box-Pierce rejette le bruit blanc des residus (p=%.3f) : AR(%d) insuffisant" % (p_bp, p_hat))
                if branche == "AR":
                    branche = "?"

        # Le verdict n'est rendu que si la branche a le droit de conclure :
        # une strategie 'NS' ou '?' SORT du domaine de validite (ni validee
        # ni rejetee) et son examen revient a l'humain.
        if alertes:
            verdict = "NS" if branche == "NS" else "?"
        else:
            verdict = "OUI" if p_corr < seuil else "non"
        alertes_par_strat[kname] = alertes

        out("%-14s %4d %5.1f | %7.3f | %5s | %7.3f %7.3f | %6.2f %2d %7.2f | %6.2f %6.0f | %8.2f %8.2f %10.2g | %7.2f | %7s" %
            (kname, t_len, couv, p_indep, branche, p_df, p_kpss, rho1, p_hat, som_phi,
             deff_t, t_eff, t_naif, t_corr, p_corr, p_bp, verdict))

    out("-" * 148)
    out("Lecture : p_indep = Box-Pierce sur la serie mensuelle BRUTE (H0 : mois independants, %d retards)." % P_MAX)
    out("          br     = branche du protocole : 'indep' (independance non rejetee -> le test 1c est valide tel quel,")
    out("                   aucune correction requise), 'AR' (autocorrelation reelle -> correction sous stationnarite),")
    out("                   '?' (diagnostic non concluant) ou 'NS' (non-stationnarite averee) -> la strategie SORT.")
    out("          p_DF   = Dickey-Fuller, H0 'racine unite' -> petit = stationnaire (condition du test remplie).")
    out("          p_KPSS = KPSS, H0 'stationnaire' -> grand = stationnaire (valeurs bornees a [0.01, 0.1]).")
    out("          rho1   = autocorrelation d'ordre 1 de la serie mensuelle (0 = mois independants, hypothese de 1c).")
    out("          p      = ordre AR choisi par coupure du PACF (|tau(h)| > 1.96/sqrt(T)), Phi estimes par Yule-Walker.")
    out("          DEFF_t = gamma_lr / gamma(0) : combien de fois la variance de la moyenne est sous-estimee par 1c ;")
    out("                   gamma_lr = sigma2_eta/(1 - somme Phi)^2 (variance de long terme de l'AR), T_eff = T/DEFF_t.")
    out("          t_corr, p_corr = Student sur la moyenne mensuelle avec erreur-type sqrt(gamma_lr/T), df = T_eff - 1.")
    out("          p_BP   = Box-Pierce sur les residus de l'AR (H0 bruit blanc) : > 0.05 = le modele AR suffit,")
    out("                   la correction de variance est donc fondee.")
    out("          verdict OUI = p_corr < seuil Bonferroni (porte 'mois' fermee, autocorrelation comprise).")
    out("          verdict ?   = diagnostic non concluant (DF/KPSS divergent, ou AR insuffisant) : la strategie")
    out("                        sort SANS etre rejetee -> examen humain (voir le bloc d'alertes ci-dessous).")
    out("          verdict NS  = non-stationnarite averee (DF et KPSS concordent) : hors du domaine de la methode.")
    out("          Limite : mois sans trade traites comme consecutifs (couverture < 100 %, surtout rsi_strict).")

    # --- bloc d'alertes : conditions d'application non remplies ------------
    signalees = {k: v for k, v in alertes_par_strat.items() if v}
    out()
    if signalees:
        out("!" * 132)
        out("ALERTES - %d strategie(s) hors du domaine de validite de la methode :" % len(signalees))
        for kname, msgs in signalees.items():
            for m in msgs:
                out("  [%-14s] %s" % (kname, m))
        out("Ces strategies ne sont ni validees ni rejetees : la correction d'autocorrelation n'a pas de sens pour elles.")
        out("!" * 132)
    else:
        out("Aucune alerte : toutes les strategies remplissent les conditions d'application (stationnarite, T, Box-Pierce).")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("")
    out("-> ecrit dans %s" % OUT)


if __name__ == "__main__":
    main()
