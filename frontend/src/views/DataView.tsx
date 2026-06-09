import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type DetectionFilters } from "../api";
import { Card, Stat } from "../components/Layout";

const PAGE = 50;
// Colonnes affichées en pourcentage.
const PCT_COLS = new Set([
  "return_gross",
  "return_net",
  "bh_return_window",
  "trade_drawdown",
  "gap_bh_return",
]);
// Colonnes colorées par signe = TON P&L (vert gain / rouge perte).
const SIGN_COLS = new Set(["return_gross", "return_net", "trade_drawdown"]);

const fmtCell = (col: string, v: string | number) => {
  if (v == null) return "—";
  if (PCT_COLS.has(col) && typeof v === "number") return `${(v * 100).toFixed(2)}%`;
  if (col === "direction") return v === 1 ? "long" : "short";
  return String(v);
};

export function DataView() {
  const summaryQ = useQuery({
    queryKey: ["dataSummary"],
    queryFn: () => api.dataSummary(),
    retry: false,
  });

  const [filters, setFilters] = useState<DetectionFilters>({});
  const [offset, setOffset] = useState(0);

  const pageQ = useQuery({
    queryKey: ["detections", filters, offset],
    queryFn: () => api.dataDetections({ ...filters, limit: PAGE, offset }),
    retry: false,
    enabled: !summaryQ.isError,
  });

  const setFilter = (k: keyof DetectionFilters, v: string | undefined) => {
    setOffset(0);
    setFilters((f) => ({ ...f, [k]: v || undefined }));
  };

  if (summaryQ.isError)
    return (
      <div className="max-w-3xl mx-auto">
        <Card title="Base de détections">
          <p className="text-loss text-sm mb-2">
            Base absente ou backend injoignable.
          </p>
          <p className="text-muted text-sm">
            Génère-la côté backend : <code>python -m charts.build_db</code> (scan du
            S&P 500), puis recharge.
          </p>
        </Card>
      </div>
    );

  const s = summaryQ.data;
  const page = pageQ.data;
  const totalFiltered = page?.total ?? 0;

  return (
    <div className="space-y-5">
      {/* Vue d'ensemble de la base */}
      <Card title="Base de détections — ce que contient ta base">
        {s && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Stat label="Trades" value={s.total.toLocaleString("fr-FR")} />
            <Stat label="Titres" value={String(s.n_tickers)} />
            <Stat label="Période" value={`${s.date_min} → ${s.date_max}`} />
            <Stat label="Version params" value={s.params_version.join(", ")} />
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <Breakdown title="Par stratégie" items={s?.by_strategy} active={filters.strategy} onPick={(k) => setFilter("strategy", k)} />
          <Breakdown title="Par régime" items={s?.by_regime} active={filters.regime} onPick={(k) => setFilter("regime", k)} />
          <Breakdown title="Par secteur" items={s?.by_sector} active={filters.sector} onPick={(k) => setFilter("sector", k)} />
        </div>
      </Card>

      {/* Filtres + table */}
      <Card
        title="Trades (filtrable)"
        right={
          <div className="flex items-center gap-2">
            <input
              placeholder="Ticker…"
              value={filters.ticker ?? ""}
              onChange={(e) => setFilter("ticker", e.target.value)}
              className="w-24 bg-panel2 border border-border rounded px-2 py-1 text-sm uppercase"
            />
            {(filters.strategy || filters.regime || filters.sector || filters.ticker) && (
              <button
                onClick={() => {
                  setFilters({});
                  setOffset(0);
                }}
                className="text-xs text-muted hover:text-text px-2 py-1"
              >
                ✕ filtres
              </button>
            )}
          </div>
        }
      >
        <div className="text-xs text-muted mb-2 space-y-1">
          <div>
            {totalFiltered.toLocaleString("fr-FR")} trade(s) — clique un libellé
            ci-dessus pour filtrer.
          </div>
          <div>
            <b>return_net</b> = ton rendement (frais déduits). <b>bh_return_window</b> =
            ce que « ne rien faire » (buy & hold) aurait fait <i>pendant</i> le trade
            (pertinent pour les signaux d'évitement). <b>gap_bh_return</b> = ce que le
            marché a fait <i>pendant que tu étais HORS marché après ce trade</i> :{" "}
            <b>négatif = chute évitée</b> (bon pour une stratégie d'entrée),{" "}
            <b>positif = hausse manquée</b> (mauvais). C'est là que se joue la vraie
            différence avec le buy & hold.
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs tabular-nums">
            <thead>
              <tr className="text-muted uppercase tracking-wide text-left">
                {(page?.columns ?? []).map((c) => (
                  <th key={c} className="font-medium py-1.5 px-2 whitespace-nowrap">
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(page?.rows ?? []).map((row, i) => (
                <tr key={i} className="border-t border-border">
                  {(page?.columns ?? []).map((c) => (
                    <td
                      key={c}
                      className={`py-1.5 px-2 whitespace-nowrap ${
                        SIGN_COLS.has(c) && typeof row[c] === "number"
                          ? (row[c] as number) >= 0
                            ? "text-gain"
                            : "text-loss"
                          : ""
                      }`}
                    >
                      {fmtCell(c, row[c])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between mt-3 text-sm">
          <button
            disabled={offset === 0}
            onClick={() => setOffset((o) => Math.max(0, o - PAGE))}
            className="px-3 py-1 rounded bg-panel2 disabled:opacity-40"
          >
            ← Précédent
          </button>
          <span className="text-muted text-xs">
            {totalFiltered === 0
              ? "0"
              : `${offset + 1}–${Math.min(offset + PAGE, totalFiltered)} / ${totalFiltered.toLocaleString("fr-FR")}`}
          </span>
          <button
            disabled={offset + PAGE >= totalFiltered}
            onClick={() => setOffset((o) => o + PAGE)}
            className="px-3 py-1 rounded bg-panel2 disabled:opacity-40"
          >
            Suivant →
          </button>
        </div>
      </Card>
    </div>
  );
}

function Breakdown({
  title,
  items,
  active,
  onPick,
}: {
  title: string;
  items?: { key: string; count: number }[];
  active?: string;
  onPick: (key: string | undefined) => void;
}) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-muted mb-1">{title}</div>
      <div className="space-y-0.5 max-h-44 overflow-y-auto">
        {(items ?? []).map((it) => (
          <button
            key={it.key}
            onClick={() => onPick(active === it.key ? undefined : it.key)}
            className={`w-full flex justify-between text-sm px-2 py-1 rounded ${
              active === it.key ? "bg-accent/15 text-accent" : "hover:bg-panel2"
            }`}
          >
            <span className="truncate">{it.key}</span>
            <span className="tabular-nums text-muted ml-2">{it.count}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
