"""Assistant conversationnel du dashboard (lecture seule), animé par un modèle LOCAL Ollama.

Rôle = couche d'INTERFACE (cf. principe modèle/exécutant) : il EXPLIQUE les stratégies
et les métriques, et RÉPOND à partir des données live qu'on lui injecte (analyse d'un
ticker + comptes). Il ne passe JAMAIS d'ordre et ne donne pas de conseil personnalisé.

Gratuit & privé : tout tourne en local via Ollama (http://localhost:11434). Si Ollama
n'est pas lancé, la route renvoie une 503 avec les instructions d'installation.
"""
from __future__ import annotations

import os

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import analysis as analysis_mod
from . import storage

router = APIRouter(prefix="/chat", tags=["chat"])

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")

SYSTEM_PROMPT = """Tu es l'assistant du dashboard « TradingMonitor ». Tu es en LECTURE SEULE.

Règles :
- Tu EXPLIQUES les stratégies et les métriques, et tu réponds à partir des DONNÉES fournies plus bas.
- Tu ne passes JAMAIS d'ordre, tu ne donnes PAS de conseil d'investissement personnalisé.
- Si une information n'est pas dans les données fournies, dis-le clairement plutôt que d'inventer.
- Réponds en français, de façon concise et pédagogique.

Glossaire :
- Croisement de moyennes mobiles (MM) : stratégie de tendance. Achat quand la MM courte passe au-dessus de la MM longue, vente à l'inverse.
- RSI : stratégie de retour à la moyenne. Achat en sortie de survente (RSI repasse au-dessus du seuil bas), vente en sortie de surachat.
- Épaule-tête-épaule (H&S) : figure chartiste. Variante inversée = haussière (achat). Variante classique = baissière (entrée en short).
- Buy & hold : acheter et garder, référence de comparaison (ne rien faire d'actif).
- Métriques : CAGR (croissance annualisée), Sharpe (rendement/risque total), Sortino (pénalise la baisse), Calmar (CAGR/pire creux), Max Drawdown (pire creux), VaR 95 % (perte quotidienne extrême), profit factor (gains/pertes), taux de réussite.
"""


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    ticker: str | None = None  # optionnel : ancre les questions sur l'analyse de ce ticker


def _pf(x) -> str:
    return "—" if x is None else f"{x:.2%}" if abs(x) < 100 else f"{x:.2f}"


async def _build_context(ticker: str | None) -> str:
    """Assemble les données live à donner au modèle : analyse d'un ticker + comptes."""
    parts: list[str] = []

    if ticker:
        try:
            r = analysis_mod.analyze(ticker)
            lines = [f"Analyse de {r['ticker']} (rendements nets de coûts) :"]
            bh = r.get("benchmark", {})
            lines.append(f"- Buy & hold : rendement total {_pf(bh.get('total_return'))}, "
                         f"Sharpe {bh.get('risk', {}).get('sharpe')}, Max DD {_pf(bh.get('risk', {}).get('max_drawdown'))}")
            for s in r["strategies"]:
                m, rk = s["metrics"], s.get("risk", {})
                lines.append(
                    f"- {s['label']} : rendement {_pf(m.get('rendement_total_cumule'))}, "
                    f"Sharpe {rk.get('sharpe')}, Sortino {rk.get('sortino')}, "
                    f"Max DD {_pf(rk.get('max_drawdown'))}, réussite {_pf(m.get('taux_reussite'))}, "
                    f"{m.get('n_trades')} trades"
                )
            parts.append("\n".join(lines))
        except Exception as e:  # noqa: BLE001
            parts.append(f"(Analyse de {ticker} indisponible : {e})")

    accounts = storage.load_accounts()
    if accounts:
        labels = ", ".join(a.get("label", "?") for a in accounts)
        parts.append(f"Comptes paper suivis : {labels}.")

    if not parts:
        return "(Aucune donnée live fournie. Réponds de façon générale et propose à l'utilisateur de choisir un ticker pour des chiffres précis.)"
    return "DONNÉES LIVE :\n" + "\n\n".join(parts)


@router.post("")
async def chat(req: ChatRequest) -> dict:
    context = await _build_context(req.ticker)
    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context}]
        + [m.model_dump() for m in req.messages]
    )
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.3},
    }
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
    except httpx.ConnectError:
        raise HTTPException(
            503,
            "Ollama injoignable. Installe-le (ollama.com), lance `ollama serve`, "
            f"puis `ollama pull {OLLAMA_MODEL}`.",
        )
    if resp.status_code == 404:
        raise HTTPException(
            503,
            f"Modèle « {OLLAMA_MODEL} » absent. Lance `ollama pull {OLLAMA_MODEL}` "
            "(ou change OLLAMA_MODEL).",
        )
    if resp.status_code != 200:
        raise HTTPException(502, f"Erreur Ollama : {resp.text[:200]}")
    return {"answer": resp.json().get("message", {}).get("content", "").strip(), "model": OLLAMA_MODEL}


@router.get("/health")
async def chat_health() -> dict:
    """Indique si Ollama est joignable et si le modèle est présent (pour l'UI)."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            models = [m["name"] for m in r.json().get("models", [])]
    except Exception:  # noqa: BLE001
        return {"ok": False, "model": OLLAMA_MODEL, "models": []}
    has = any(m == OLLAMA_MODEL or m.startswith(OLLAMA_MODEL + ":") for m in models)
    return {"ok": True, "model": OLLAMA_MODEL, "model_present": has, "models": models}
