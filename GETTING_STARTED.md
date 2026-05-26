# 🚀 Démarrer TradingMonitor sur ta machine

Guide pas-à-pas pour quelqu'un qui n'a jamais lancé d'app Python + React.
Compte sur **10 à 15 minutes** la première fois (téléchargements inclus).

> ℹ️ **Paper trading uniquement.** Aucun argent réel n'est utilisé.
> L'app est en **lecture seule** : elle observe, elle ne trade pas.

---

## 1. Ce que tu vas installer

Trois choses, une seule fois sur la machine :

1. **Python 3.11 ou plus récent** — pour faire tourner le backend (l'API qui parle à Alpaca).
2. **Node.js 18 ou plus récent** — pour faire tourner le frontend (le dashboard dans le navigateur).
3. **Git** *(optionnel)* — si tu veux cloner le projet plutôt que télécharger un zip.

### Comment vérifier ce qui est déjà installé

Ouvre un **terminal** :
- **Windows** : touche Windows → tape `powershell` → Entrée
- **macOS** : `Cmd + Espace` → tape `terminal` → Entrée
- **Linux** : tu sais.

Tape ces commandes (une à la fois) et regarde le résultat :

```bash
python --version
node --version
npm --version
```

Si une commande dit "non reconnue" ou "command not found", c'est qu'il faut installer le bout manquant :

- **Python** : https://www.python.org/downloads/ → coche bien **"Add Python to PATH"** pendant l'installation Windows.
- **Node.js** : https://nodejs.org/ → prends la version **LTS** (le gros bouton de gauche).

> ✅ **Vérification :** ferme et rouvre ton terminal après installation, puis re-teste `python --version` et `node --version`. Les deux doivent répondre une version.

---

## 2. Récupérer le code

### Option A — Tu as Git

```bash
git clone <url-du-repo> TradingMonitor
cd TradingMonitor
```

### Option B — Pas de Git

Télécharge le zip du projet, dézippe-le, puis ouvre un terminal **dans le dossier dézippé** (Windows : Shift + clic droit dans le dossier → "Ouvrir dans le terminal").

Tu dois voir ces dossiers quand tu fais `ls` (ou `dir` sous Windows) :

```
backend/  frontend/  README.md  ...
```

---

## 3. Récupérer tes clés Alpaca Paper

1. Crée un compte gratuit sur https://alpaca.markets (ou connecte-toi).
2. Va sur le **Paper Trading Dashboard** : https://app.alpaca.markets/paper/dashboard/overview
3. Sur la droite, panneau **"Your API Keys"** → clique **"Generate New Keys"** (ou "View" si tu en as déjà).
4. Note deux choses dans un coin (un fichier texte, pas un screenshot public) :
   - **API Key ID** (commence souvent par `PK...`)
   - **Secret Key** (longue chaîne) — ⚠️ elle ne s'affiche **qu'une seule fois**, sauvegarde-la.

> 💡 Tu peux créer plusieurs comptes paper si tu veux en monitorer plusieurs (un par bot).

---

## 4. Installer et lancer le backend

Le backend est l'API Python qui interroge Alpaca. Il tourne sur le **port 8000**.

### 4.1 — Ouvrir un terminal dans `backend/`

```bash
cd backend
```

### 4.2 — Créer un environnement Python isolé (venv)

C'est une bulle qui contient les libs du projet sans polluer ton système.

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> ⚠️ Si PowerShell refuse avec un message sur "scripts désactivés", lance d'abord :
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
> Réponds `O` (Oui), puis relance la commande `Activate.ps1`.

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Tu sauras que c'est activé quand ton prompt commence par `(.venv)`.

### 4.3 — Installer les dépendances

```bash
pip install -r requirements.txt
```

Ça télécharge FastAPI, httpx, etc. (~30 secondes).

### 4.4 — Lancer le backend

```bash
python run.py
```

Tu dois voir un truc du genre :

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

🎉 Le backend tourne. **Laisse ce terminal ouvert.**

> 🔎 **Test rapide :** ouvre http://127.0.0.1:8000/health dans ton navigateur, tu dois voir `{"ok":true,"ts":...}`.

---

## 5. Installer et lancer le frontend

Le frontend est le dashboard React. Il tourne sur le **port 5173**.

### 5.1 — Ouvrir un **deuxième** terminal dans `frontend/`

(Ne ferme pas celui du backend ! Ouvre une nouvelle fenêtre/onglet de terminal.)

```bash
cd frontend
```

### 5.2 — Installer les dépendances

```bash
npm install
```

Ça télécharge React, Tailwind, Recharts, etc. (~1 minute la première fois).

### 5.3 — Lancer le dashboard

```bash
npm run dev
```

Tu dois voir :

```
  VITE v5.x.x  ready in xxx ms
  ➜  Local:   http://localhost:5173/
```

🎉 Ouvre http://localhost:5173 dans ton navigateur.

---

## 6. Ajouter ton premier compte Alpaca

Dans le dashboard ouvert :

1. Clique sur **"+ Ajouter un compte"** en haut à droite.
2. Remplis :
   - **Label** : un nom lisible (ex: `Bot RSI`, `Test perso`, `momentum`)
   - **API Key** : ta clé Alpaca paper (le `PK...`)
   - **API Secret** : ta secret key Alpaca paper
   - **Base URL** : laisse `https://paper-api.alpaca.markets` (par défaut)
     - *(Si Alpaca t'a donné `https://paper-api.alpaca.markets/v2`, c'est OK aussi, le backend gère les deux.)*
3. Clique **Ajouter**.

Si tout marche :
- Tu vois ton compte apparaître comme onglet en haut.
- La **Vue d'ensemble** montre une carte avec ton equity (100 000 $ par défaut sur un compte paper neuf).
- Clique sur l'onglet de ton compte pour voir le détail (graphique, positions, ordres).

Si tu vois une **pastille rouge** sur la carte du compte → tes clés sont fausses ou ton réseau ne joint pas Alpaca. Re-vérifie API Key + Secret.

---

## 7. Au quotidien

Pour relancer l'app les fois suivantes :

**Terminal 1 — Backend**
```bash
cd backend
# Windows :
.\.venv\Scripts\Activate.ps1
# macOS/Linux :
source .venv/bin/activate

python run.py
```

**Terminal 2 — Frontend**
```bash
cd frontend
npm run dev
```

Puis ouvre http://localhost:5173.

Pour **arrêter** : `Ctrl + C` dans chaque terminal.

---

## 8. Problèmes fréquents

### "python : commande introuvable" / "command not found"
Python n'est pas installé ou pas dans le PATH. Sous Windows, réinstalle Python en cochant **"Add Python to PATH"** sur le **premier écran** de l'installeur.

### "Activate.ps1 cannot be loaded because running scripts is disabled"
Voir la note dans la section 4.2 — lance `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

### "Port 8000 already in use" / "address already in use"
Un autre process utilise le port. Soit tu le tues, soit tu lances le backend sur un autre port :
```bash
uvicorn app.main:app --reload --port 8001
```
…et tu modifies `frontend/vite.config.ts` pour proxyfier vers `8001` au lieu de `8000`.

### Le frontend affiche "Backend injoignable"
Le backend n'est pas lancé, ou il a crashé. Va voir le terminal du backend, regarde les logs.

### Pastille rouge sur ma carte compte
- Vérifie tes clés API (copie-colle attentif, pas d'espaces).
- Vérifie que la Base URL est bien `https://paper-api.alpaca.markets` (paper) et pas l'URL live.
- Test direct : ouvre http://127.0.0.1:8000/accounts/<ton_id>/summary dans ton navigateur, lis le message d'erreur.

### "Module not found" en lançant le backend
Tu as oublié d'activer le venv avant `pip install`. Refais la section 4.2 puis 4.3.

### Le dashboard se met à jour quand ?
Toutes les **5 secondes** automatiquement. Tu n'as pas besoin de rafraîchir la page.

---

## 9. Où sont mes données ?

- **Clés API** : `backend/data/accounts.json` (en clair, sur ta machine uniquement, jamais envoyées ailleurs que vers Alpaca).
- **Historique equity 5s** : `backend/data/snapshots.db` (SQLite, rétention 48h).

Pour supprimer **tous tes comptes** d'un coup : ferme le backend, supprime `backend/data/accounts.json` et `backend/data/snapshots.db`, relance.

---

## 10. La suite

- Configure tes agents n8n pour qu'ils tradent sur les comptes paper dont tu as les clés.
- Pour distinguer plusieurs bots sur le **même** compte Alpaca : préfixe leur `client_order_id` (ex: `rsi-bot_<uuid>`). Le dashboard affichera `rsi-bot` dans la colonne **Agent**.
- Sinon (recommandé), 1 compte paper = 1 bot, et le label du compte sert de nom d'agent.

Bon monitoring ! 📈
