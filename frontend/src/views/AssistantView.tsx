import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type ChatMsg } from "../api";
import { Card } from "../components/Layout";

/** Assistant IA local (Ollama), lecture seule : explique stratégies/métriques et
 *  répond à partir des données du dashboard. Ne passe aucun ordre. */
export function AssistantView() {
  const health = useQuery({
    queryKey: ["chatHealth"],
    queryFn: () => api.chatHealth(),
    refetchInterval: 15_000,
  });
  const defaultsQ = useQuery({
    queryKey: ["analysisDefaults"],
    queryFn: () => api.analysisDefaults(),
  });

  const [ticker, setTicker] = useState("");
  const [input, setInput] = useState("");
  const [msgs, setMsgs] = useState<ChatMsg[]>([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, pending]);

  const send = async () => {
    const text = input.trim();
    if (!text || pending) return;
    const next = [...msgs, { role: "user" as const, content: text }];
    setMsgs(next);
    setInput("");
    setError(null);
    setPending(true);
    try {
      const r = await api.chat(next, ticker);
      setMsgs([...next, { role: "assistant", content: r.answer }]);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Erreur inconnue lors de l'appel au modèle.",
      );
    } finally {
      setPending(false);
    }
  };

  const offline = health.data && !health.data.ok;
  const modelMissing = health.data?.ok && health.data.model_present === false;

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <Card title="Assistant IA (local · lecture seule)">
        <div className="flex flex-wrap items-center gap-3 text-sm">
          <span className="text-muted">Modèle :</span>
          <code className="text-accent">{health.data?.model ?? "…"}</code>
          <span
            className={`inline-flex items-center gap-1.5 ${
              offline ? "text-loss" : modelMissing ? "text-amber-400" : "text-gain"
            }`}
          >
            <span className="w-2 h-2 rounded-full" style={{ background: "currentColor" }} />
            {offline ? "Ollama hors ligne" : modelMissing ? "modèle non installé" : "prêt"}
          </span>
          <div className="ml-auto flex items-center gap-2">
            <label className="text-muted text-xs">Ancrer sur :</label>
            <select
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              className="bg-panel2 border border-border rounded px-2 py-1 text-sm"
            >
              <option value="">aucun ticker</option>
              {(defaultsQ.data?.tickers ?? []).map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
        </div>
        <p className="text-xs text-muted mt-2">
          Il explique les stratégies/métriques et répond à partir des données du
          dashboard. Choisis un ticker pour des chiffres précis. Il ne passe jamais
          d'ordre.
        </p>
      </Card>

      {offline && (
        <div className="bg-panel border border-border rounded-xl p-4 text-sm">
          <p className="text-loss mb-2">Ollama n'est pas lancé.</p>
          <ol className="list-decimal list-inside text-muted space-y-1">
            <li>Installe Ollama depuis ollama.com</li>
            <li>
              Lance le serveur : <code>ollama serve</code>
            </li>
            <li>
              Récupère le modèle :{" "}
              <code>ollama pull {health.data?.model ?? "qwen2.5:7b"}</code>
            </li>
          </ol>
        </div>
      )}

      <Card>
        <div className="h-[48vh] overflow-y-auto space-y-3 pr-1">
          {msgs.length === 0 && (
            <div className="text-muted text-sm space-y-1">
              <p>Exemples de questions :</p>
              <ul className="list-disc list-inside">
                <li>« C'est quoi le Sharpe, simplement ? »</li>
                <li>« Sur AAPL, quelle stratégie a le meilleur Sharpe ? » (choisis le ticker)</li>
                <li>« Pourquoi l'épaule-tête-épaule short perd souvent ? »</li>
              </ul>
            </div>
          )}
          {msgs.map((m, i) => (
            <div
              key={i}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-xl px-3 py-2 text-sm whitespace-pre-wrap ${
                  m.role === "user"
                    ? "bg-accent/15 text-text"
                    : "bg-panel2 text-text"
                }`}
              >
                {m.content}
              </div>
            </div>
          ))}
          {pending && (
            <div className="flex justify-start">
              <div className="bg-panel2 text-muted rounded-xl px-3 py-2 text-sm">
                réflexion… (le modèle local peut être lent)
              </div>
            </div>
          )}
          {error && <div className="text-loss text-sm">{error}</div>}
          <div ref={endRef} />
        </div>

        <div className="flex gap-2 mt-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            rows={2}
            placeholder="Pose ta question… (Entrée pour envoyer, Maj+Entrée = nouvelle ligne)"
            className="flex-1 bg-panel2 border border-border rounded px-3 py-2 text-sm resize-none"
          />
          <button
            onClick={send}
            disabled={pending || !input.trim()}
            className="px-4 bg-accent/15 text-accent rounded hover:bg-accent/25 text-sm disabled:opacity-50"
          >
            Envoyer
          </button>
        </div>
      </Card>
    </div>
  );
}
