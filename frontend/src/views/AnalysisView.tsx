import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Brush,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceDot,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api, type Analysis, type Oscillator, type Overlay } from "../api";
import { Card } from "../components/Layout";
import { fmtNum } from "../format";

const BH_KEY = "__bh";
const BH_COLOR = "#64748b";
const pct = (n: number | undefined | null) =>
  n == null ? "—" : `${(n * 100).toFixed(1)}%`;

export function AnalysisView() {
  const defaultsQ = useQuery({
    queryKey: ["analysisDefaults"],
    queryFn: () => api.analysisDefaults(),
  });

  const [ticker, setTicker] = useState("AAPL");
  const [short, setShort] = useState(50);
  const [long, setLong] = useState(200);
  // Stratégies/benchmark affichés (indépendant du produit). Rien d'imposé en permanence.
  const [shown, setShown] = useState<Set<string>>(new Set());

  const mut = useMutation<Analysis, Error>({
    mutationFn: () => api.analyze(ticker.trim().toUpperCase(), short, long),
    onSuccess: (data) => {
      // À chaque analyse, on affiche par défaut toutes les stratégies + le buy & hold.
      setShown(new Set([...data.strategies.map((s) => s.key), BH_KEY]));
    },
  });

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (ticker.trim()) mut.mutate();
  };

  const toggle = (key: string) =>
    setShown((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });

  const data = mut.data;

  return (
    <div className="space-y-6">
      {/* Produit + paramètres */}
      <Card title="Analyse technique">
        <form onSubmit={submit} className="flex flex-wrap items-end gap-3">
          <Field label="Produit (ticker)">
            <TickerCombo
              value={ticker}
              onChange={setTicker}
              options={defaultsQ.data?.tickers ?? []}
            />
          </Field>
          <Field label="MM courte">
            <input
              type="number"
              min={2}
              value={short}
              onChange={(e) => setShort(Number(e.target.value))}
              className="w-24 bg-panel2 border border-border rounded px-2 py-1.5 text-sm"
            />
          </Field>
          <Field label="MM longue">
            <input
              type="number"
              min={3}
              value={long}
              onChange={(e) => setLong(Number(e.target.value))}
              className="w-24 bg-panel2 border border-border rounded px-2 py-1.5 text-sm"
            />
          </Field>
          <button
            type="submit"
            disabled={mut.isPending}
            className="px-4 py-1.5 bg-accent/15 text-accent rounded hover:bg-accent/25 text-sm disabled:opacity-50"
          >
            {mut.isPending ? "Analyse…" : "Analyser"}
          </button>
        </form>
        <p className="text-xs text-muted mt-2">
          Données journalières (yfinance), prix ajustés depuis 2010.
        </p>
      </Card>

      {mut.isError && (
        <div className="text-loss text-sm">
          Erreur : {mut.error.message}. Le ticker existe-t-il ? Backend lancé ?
        </div>
      )}
      {mut.isPending && (
        <div className="text-muted text-sm">
          Téléchargement et analyse de {ticker.toUpperCase()}…
        </div>
      )}

      {data && (
        <StrategiesSection data={data} shown={shown} toggle={toggle} />
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */

function StrategiesSection({
  data,
  shown,
  toggle,
}: {
  data: Analysis;
  shown: Set<string>;
  toggle: (key: string) => void;
}) {
  return (
    <>
      {/* Sélection des stratégies à afficher (+ buy & hold) */}
      <Card title="Stratégies — coche pour afficher rendement + courbes">
        <div className="space-y-1">
          {data.strategies.map((s) => (
            <Row
              key={s.key}
              checked={shown.has(s.key)}
              onToggle={() => toggle(s.key)}
              color={s.color}
              label={s.label}
              shownDetail={
                shown.has(s.key)
                  ? `${pct(s.metrics.rendement_total_cumule)} · ${pct(
                      s.metrics.taux_reussite,
                    )} réussite · ${s.metrics.n_trades} trades`
                  : null
              }
            />
          ))}
          <Row
            checked={shown.has(BH_KEY)}
            onToggle={() => toggle(BH_KEY)}
            color={BH_COLOR}
            label="Buy & hold (acheter et garder)"
            shownDetail={
              shown.has(BH_KEY) ? pct(data.benchmark.total_return) : null
            }
          />
        </div>
        <p className="text-xs text-muted mt-2">
          Rendement des stratégies = trades clôturés (réalisés), comparable entre
          stratégies. ⚠️ Un seul titre ne prouve rien.
        </p>
      </Card>

      {/* Graphique 1 : courbes de rendement comparées */}
      <Card title="Courbes de rendement (1$ investi, base 100)">
        <EquityChart data={data} shown={shown} />
      </Card>

      {/* Graphique 2 : cours du produit + repères des stratégies */}
      <Card title={`Cours de ${data.ticker} + repères`}>
        <PriceChart data={data} shown={shown} />
        <p className="text-xs text-muted mt-2">
          Glisse le curseur pour lire les valeurs ; glisse les poignées du bas
          pour zoomer. 🟢 achat · 🔴 vente · 🟢⬛ position ouverte.
        </p>
      </Card>

      {/* Panneau RSI : visible seulement si une stratégie à oscillateur est cochée */}
      <RsiPanel data={data} shown={shown} />
    </>
  );
}

/** Panneau oscillateur RSI (0-100) avec les droites de seuils des variantes cochées.
 *  Les variantes partagent la même courbe RSI(14) -> on ne la trace qu'une fois ;
 *  seuls les seuils (30/70, 20/80…) diffèrent et sont dédupliqués. */
function RsiPanel({ data, shown }: { data: Analysis; shown: Set<string> }) {
  const oscStrategies = data.strategies.filter(
    (s) => shown.has(s.key) && s.oscillator,
  );
  if (oscStrategies.length === 0) return null;

  // Courbes RSI distinctes (par nom : RSI14 partagé entre variantes -> une seule).
  const byName = new Map<string, Oscillator>();
  for (const s of oscStrategies) {
    if (s.oscillator && !byName.has(s.oscillator.name)) {
      byName.set(s.oscillator.name, s.oscillator);
    }
  }
  const lines = [...byName.values()];

  // Seuils à tracer = union dédupliquée des bornes des variantes cochées.
  const thresholds = [
    ...new Set(oscStrategies.flatMap((s) => [s.oscillator!.lower, s.oscillator!.upper])),
  ].sort((a, b) => a - b);

  const rows = data.dates.map((d, i) => {
    const row: Record<string, number | string | null> = { date: d };
    for (const o of lines) row[o.name] = o.data[i] ?? null;
    return row;
  });

  return (
    <Card title="RSI — surachat / survente">
      <div
        className="rounded-lg p-2"
        style={{ width: "100%", height: 220, background: CHART_BG }}
      >
        <ResponsiveContainer>
          <LineChart data={rows} margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
            <CartesianGrid stroke={GRID} vertical={false} />
            <XAxis dataKey="date" minTickGap={70} tick={{ fontSize: 11, fill: AXIS }} stroke={AXIS_LINE} />
            <YAxis domain={[0, 100]} ticks={[0, ...thresholds, 100]} tick={{ fontSize: 11, fill: AXIS }} stroke={AXIS_LINE} width={52} />
            <Tooltip
              contentStyle={tooltipStyle}
              labelFormatter={(l) => `Date : ${l}`}
              formatter={(v, n) => [v == null ? "—" : fmtNum(Number(v), 1), n as string]}
            />
            {thresholds.map((t) => (
              <ReferenceLine
                key={t}
                y={t}
                stroke={t >= 50 ? "#ef4444" : "#22c55e"}
                strokeDasharray="4 4"
                label={{ value: String(t), position: "right", fontSize: 11, fill: AXIS }}
              />
            ))}
            {lines.map((o) => (
              <Line key={o.name} type="monotone" dataKey={o.name} name={o.name} stroke="#7c3aed" strokeWidth={1.4} dot={false} connectNulls isAnimationActive={false} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-muted mt-2">
        Droites = seuils des variantes cochées. 🟢 achat quand le RSI{" "}
        <b>repasse au-dessus</b> du seuil bas · 🔴 vente quand il{" "}
        <b>repasse sous</b> le seuil haut.
      </p>
    </Card>
  );
}

function Row({
  checked,
  onToggle,
  color,
  label,
  shownDetail,
}: {
  checked: boolean;
  onToggle: () => void;
  color: string;
  label: string;
  shownDetail: string | null;
}) {
  return (
    <label className="flex items-center gap-3 py-1 cursor-pointer">
      <input type="checkbox" checked={checked} onChange={onToggle} />
      <span
        className="inline-block w-3 h-3 rounded-sm"
        style={{ background: color }}
      />
      <span className="text-sm">{label}</span>
      {shownDetail && (
        <span className="text-sm text-muted ml-auto tabular-nums">
          {shownDetail}
        </span>
      )}
    </label>
  );
}

/* ------------------------- Graphiques ----------------------------- */

const CHART_BG = "#ffffff";
const GRID = "#e2e8f0";
const AXIS = "#475569";
const AXIS_LINE = "#cbd5e1";

const tooltipStyle = {
  background: "#ffffff",
  border: "1px solid #e2e8f0",
  borderRadius: 8,
  fontSize: 12,
  color: "#111827",
} as const;

function EquityChart({ data, shown }: { data: Analysis; shown: Set<string> }) {
  const rows = useMemo(() => {
    return data.dates.map((d, i) => {
      const row: Record<string, number | string | null> = { date: d };
      if (shown.has(BH_KEY)) row[BH_KEY] = data.benchmark.equity?.[i] ?? null;
      for (const s of data.strategies) {
        if (shown.has(s.key)) row[s.key] = s.equity[i] ?? null;
      }
      return row;
    });
  }, [data, shown]);

  return (
    <div
      className="rounded-lg p-2"
      style={{ width: "100%", height: 420, background: CHART_BG }}
    >
      <ResponsiveContainer>
        <LineChart data={rows} margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
          <CartesianGrid stroke={GRID} vertical={false} />
          <XAxis dataKey="date" minTickGap={70} tick={{ fontSize: 11, fill: AXIS }} stroke={AXIS_LINE} />
          <YAxis tick={{ fontSize: 11, fill: AXIS }} stroke={AXIS_LINE} width={52} domain={["auto", "auto"]} tickFormatter={(v) => fmtNum(v, 0)} />
          <Tooltip
            contentStyle={tooltipStyle}
            labelFormatter={(l) => `Date : ${l}`}
            formatter={(v, n) => [v == null ? "—" : fmtNum(Number(v)), n as string]}
          />
          <Legend />
          {shown.has(BH_KEY) && (
            <Line type="monotone" dataKey={BH_KEY} name="Buy & hold" stroke={BH_COLOR} strokeWidth={1.4} dot={false} connectNulls isAnimationActive={false} />
          )}
          {data.strategies.map(
            (s) =>
              shown.has(s.key) && (
                <Line key={s.key} type="monotone" dataKey={s.key} name={s.label} stroke={s.color} strokeWidth={1.6} dot={false} connectNulls isAnimationActive={false} />
              ),
          )}
          <Brush dataKey="date" height={26} stroke="#2563eb" fill="#f1f5f9" travellerWidth={8} tickFormatter={() => ""} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function PriceChart({ data, shown }: { data: Analysis; shown: Set<string> }) {
  const shownStrategies = data.strategies.filter((s) => shown.has(s.key));

  // Dédupe les overlays par nom : une même moyenne (ex. MM200) peut venir de
  // plusieurs stratégies cochées (croisement MM + RSI+filtre) -> on ne la trace qu'une fois.
  const overlays: Overlay[] = [];
  const seenOverlay = new Set<string>();
  for (const s of shownStrategies) {
    for (const o of s.overlays) {
      if (!seenOverlay.has(o.name)) {
        seenOverlay.add(o.name);
        overlays.push(o);
      }
    }
  }

  const rows = useMemo(() => {
    return data.dates.map((d, i) => {
      const row: Record<string, number | string | null> = {
        date: d,
        close: data.close[i] ?? null,
      };
      for (const o of overlays) row[o.key] = o.data[i] ?? null;
      return row;
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, shown]);

  return (
    <div
      className="rounded-lg p-2"
      style={{ width: "100%", height: 460, background: CHART_BG }}
    >
      <ResponsiveContainer>
        <LineChart data={rows} margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
          <CartesianGrid stroke={GRID} vertical={false} />
          <XAxis dataKey="date" minTickGap={70} tick={{ fontSize: 11, fill: AXIS }} stroke={AXIS_LINE} />
          <YAxis tick={{ fontSize: 11, fill: AXIS }} stroke={AXIS_LINE} width={52} domain={["auto", "auto"]} tickFormatter={(v) => fmtNum(v, 0)} />
          <Tooltip
            contentStyle={tooltipStyle}
            labelFormatter={(l) => `Date : ${l}`}
            formatter={(v, n) => [v == null ? "—" : fmtNum(Number(v)), n as string]}
          />
          <Legend />
          <Line type="monotone" dataKey="close" name="Cours" stroke="#111827" strokeWidth={1.3} dot={false} isAnimationActive={false} />
          {overlays.map((o) => (
            <Line key={o.key} type="monotone" dataKey={o.key} name={o.name} stroke={o.color} strokeWidth={1.5} dot={false} connectNulls isAnimationActive={false} />
          ))}
          {shownStrategies.flatMap((s) => [
            ...s.trades.map((t, i) => (
              <ReferenceDot key={`${s.key}-e${i}`} x={t.entry_date} y={t.entry_price} r={4} fill="#22c55e" stroke="none" />
            )),
            ...s.trades.map((t, i) => (
              <ReferenceDot key={`${s.key}-x${i}`} x={t.exit_date} y={t.exit_price} r={4} fill="#ef4444" stroke="none" />
            )),
            s.open_position ? (
              <ReferenceDot key={`${s.key}-open`} x={s.open_position.entry_date} y={s.open_position.entry_price} r={6} fill="#22c55e" stroke="#000" strokeWidth={2} />
            ) : null,
          ])}
          <Brush dataKey="date" height={26} stroke="#2563eb" fill="#f1f5f9" travellerWidth={8} tickFormatter={() => ""} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

/* ------------------------- Champs / combo ------------------------- */

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs uppercase tracking-wide text-muted">{label}</span>
      {children}
    </div>
  );
}

/** Sélecteur de ticker : ▼ affiche TOUTES les valeurs ; taper filtre. */
function TickerCombo({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: string[];
}) {
  const [open, setOpen] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const q = value.trim().toUpperCase();
  const list = showAll ? options : options.filter((o) => o.includes(q));

  return (
    <div ref={ref} className="relative">
      <div className="flex">
        <input
          value={value}
          onChange={(e) => {
            onChange(e.target.value);
            setShowAll(false);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          className="w-28 bg-panel2 border border-border rounded-l px-2 py-1.5 text-sm uppercase"
          placeholder="AAPL"
        />
        <button
          type="button"
          aria-label="Voir tous les tickers"
          onClick={() => {
            setShowAll(true);
            setOpen((o) => !o);
          }}
          className="px-2 border border-l-0 border-border rounded-r bg-panel2 text-muted hover:text-text text-xs"
        >
          ▼
        </button>
      </div>
      {open && list.length > 0 && (
        <ul className="absolute z-20 mt-1 w-40 max-h-56 overflow-auto bg-panel border border-border rounded shadow-lg">
          {list.map((o) => (
            <li key={o}>
              <button
                type="button"
                onClick={() => {
                  onChange(o);
                  setOpen(false);
                }}
                className={`w-full text-left px-2 py-1.5 text-sm hover:bg-panel2 ${
                  o === q ? "text-accent" : ""
                }`}
              >
                {o}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
