# TradingMonitor

Dashboard local **lecture seule** pour monitorer plusieurs comptes Alpaca **paper trading**
en temps réel. Conçu pour observer ce que font des agents automatisés (n8n) qui tradent
sur ces comptes — pas pour passer d'ordres.

- Backend : Python 3.11 + FastAPI + httpx (REST Alpaca async) + SQLite (snapshots equity)
- Frontend : Vite + React + TypeScript + Tailwind + Recharts + TanStack Query
- Multi-comptes natif, vue par compte + vue d'ensemble agrégée
- Refresh live toutes les 5s
- Aucun ordre n'est envoyé depuis l'app

> ⚠️ **Paper uniquement.** Le `base_url` par défaut est `https://paper-api.alpaca.markets`.
> Les clés API restent côté backend dans `backend/data/accounts.json` (gitignored).

---

## 1. Installation

### Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

---

## 2. Lancement

Deux terminaux :

**Terminal 1 — backend (port 8000)**

```bash
cd backend
python run.py
# ou: uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend (port 5173)**

```bash
cd frontend
npm run dev
```

Ouvre http://localhost:5173.

Le frontend proxy `/api/*` vers `http://127.0.0.1:8000` (cf. `vite.config.ts`).

---

## 3. Ajouter un compte paper

Deux options :

### Depuis l'UI (recommandé)

Clique sur **+ Ajouter un compte** dans la barre du haut. Renseigne :

- **Label** : nom lisible, idéalement le nom de l'agent (ex: `rsi-bot`, `momentum`)
- **API Key** / **API Secret** : depuis https://app.alpaca.markets/paper/dashboard/overview
- **Base URL** : laisse `https://paper-api.alpaca.markets`

### En éditant le fichier directement

```jsonc
// backend/data/accounts.json
[
  {
    "id": "rsi",
    "label": "Bot RSI",
    "api_key": "PKxxxxxxxxxxxxxxxxxx",
    "api_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "base_url": "https://paper-api.alpaca.markets"
  }
]
```

Voir `backend/data/accounts.example.json` comme modèle.

---

## 4. Convention d'attribution par agent

Le dashboard supporte 2 modèles :

1. **1 compte = 1 agent** (le plus simple) — le `label` du compte = nom de l'agent.
   Rien à faire de spécial.
2. **Plusieurs agents sur le même compte** — chaque ordre Alpaca a un champ
   `client_order_id` librement settable. Si tes workflows n8n le préfixent avec
   le nom de l'agent suivi d'un underscore (ex: `rsi-bot_42a9...`), le dashboard
   parse ce préfixe et l'affiche dans la colonne **Agent** des tableaux d'ordres.

---

## 5. API backend (lecture seule)

| Méthode | Route | Description |
|--------|-------|-------------|
| GET | `/accounts` | Liste les comptes (sans les secrets) |
| POST | `/accounts` | Ajoute un compte `{label, api_key, api_secret, base_url?}` |
| DELETE | `/accounts/{id}` | Supprime un compte |
| GET | `/accounts/{id}/summary` | equity, cash, buying_power, P&L jour & total |
| GET | `/accounts/{id}/positions` | positions ouvertes |
| GET | `/accounts/{id}/orders?limit=50` | ordres récents (avec agent déduit) |
| GET | `/accounts/{id}/history?period=1M` | courbe equity (Alpaca portfolio/history) |
| GET | `/overview` | Vue agrégée tous comptes (asyncio.gather) |
| GET | `/health` | Liveness |

Les appels Alpaca multi-comptes sont systématiquement parallélisés via
`asyncio.gather`. Un compte en erreur (clés invalides, API down) est marqué
`statut_connexion = "erreur"` dans `/overview` sans casser les autres.

---

## 6. Snapshots equity locaux

Un scheduler `asyncio` côté backend prend un snapshot de l'`equity` de chaque
compte toutes les **5 secondes** et le stocke dans `backend/data/snapshots.db`
(SQLite). Sur la période `1D`, ces snapshots sont fusionnés avec
`portfolio/history` pour une courbe intraday plus lisse. Rétention : 48h.

---

## 7. Structure du repo

```
backend/
  app/
    main.py            FastAPI + routes
    alpaca_client.py   wrapper REST async (httpx)
    services.py        shaping des réponses + agrégation
    scheduler.py       snapshots 5s -> SQLite
    storage.py         accounts.json + SQLite
  data/
    accounts.json      (créé au runtime, gitignored)
    snapshots.db       (créé au runtime, gitignored)
  requirements.txt
  run.py
frontend/
  src/
    api.ts             client REST typé
    App.tsx            shell + onglets
    views/
      OverviewView.tsx vue d'ensemble agrégée
      AccountView.tsx  vue par compte
    components/        Card / EquityChart / AddAccountModal / ...
```

---

## 8. Notes

- Lecture seule : aucun bouton ne passe / annule un ordre.
- Marché fermé : Alpaca renvoie les dernières valeurs connues, le dashboard
  reste fonctionnel.
- Le P&L total est calculé avec un capital de départ de 100 000 USD (valeur
  par défaut d'un compte paper). Si tu as ajouté/retiré du cash, c'est une
  approximation.
- Stockage en clair des clés API : à n'utiliser que sur ta machine locale.
