import { useQueries, useQuery } from "@tanstack/react-query";
import { api } from "../api";
import { Card, LiveDot, Stat } from "../components/Layout";
import { fmtMoney, fmtNum, fmtPct, gainLoss } from "../format";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const REFETCH = 5000;
const PALETTE = [
  "#60a5fa",
  "#22c55e",
  "#f59e0b",
  "#ef4444",
  "#a78bfa",
  "#14b8a6",
  "#f472b6",
  "#facc15",
];

export function OverviewView({
  onSelectAccount,
}: {
  onSelectAccount: (id: string) => void;
}) {
  const ovQ = useQuery({
    queryKey: ["overview"],
    queryFn: () => api.overview(),
    refetchInterval: REFETCH,
  });

  const accountIds = (ovQ.data?.par_compte ?? []).map((a) => a.id);
  const histories = useQueries({
    queries: accountIds.map((id) => ({
      queryKey: ["history", id, "1M"],
      queryFn: () => api.history(id, "1M"),
      refetchInterval: 60_000,
    })),
  });

  const ov = ovQ.data;

  // Build normalized comparison series
  const compData = (() => {
    if (!ov) return [];
    const series: Record<string, Record<number, number>> = {};
    const allTs = new Set<number>();
    ov.par_compte.forEach((acc, i) => {
      const h = histories[i]?.data;
      if (!h || h.points.length === 0) return;
      const base = h.points[0].equity || 1;
      const map: Record<number, number> = {};
      h.points.forEach((p) => {
        map[p.ts] = (p.equity / base) * 100;
        allTs.add(p.ts);
      });
      series[acc.label] = map;
    });
    return Array.from(allTs)
      .sort((a, b) => a - b)
      .map((ts) => {
        const row: Record<string, number | string> = { ts: ts * 1000 };
        for (const k of Object.keys(series)) {
          if (series[k][ts] !== undefined) row[k] = series[k][ts];
        }
        return row;
      });
  })();

  const seriesKeys = Object.keys(
    compData.reduce<Record<string, true>>((acc, row) => {
      Object.keys(row).forEach((k) => {
        if (k !== "ts") acc[k] = true;
      });
      return acc;
    }, {}),
  );

  return (
    <div className="flex flex-col gap-4">
      <Card right={<LiveDot />}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <Stat
            label="Equity totale"
            value={ov ? fmtMoney(ov.total_equity) : "—"}
          />
          <Stat
            label="Cash total"
            value={ov ? fmtMoney(ov.total_cash) : "—"}
          />
          <Stat
            label="P&L du jour cumulé"
            value={ov ? fmtMoney(ov.total_pnl_today) : "—"}
            sub={ov ? fmtPct(ov.total_pnl_today_pct) : undefined}
            tone={ov ? (ov.total_pnl_today >= 0 ? "gain" : "loss") : "neutral"}
          />
          <Stat
            label="P&L total cumulé"
            value={ov ? fmtMoney(ov.total_pnl_total) : "—"}
            tone={ov ? (ov.total_pnl_total >= 0 ? "gain" : "loss") : "neutral"}
          />
        </div>
      </Card>

      <Card title="Comptes">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {(ov?.par_compte ?? []).map((a) => (
            <button
              key={a.id}
              onClick={() => onSelectAccount(a.id)}
              className="text-left bg-panel2 border border-border rounded-xl p-4 hover:border-accent transition"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium">{a.label}</div>
                <span
                  className={`w-2.5 h-2.5 rounded-full ${
                    a.statut_connexion === "ok" ? "bg-gain" : "bg-loss"
                  }`}
                  title={a.statut_connexion}
                />
              </div>
              {a.statut_connexion === "erreur" ? (
                <div className="text-loss text-xs">
                  {a.error ?? "erreur de connexion"}
                </div>
              ) : (
                <>
                  <div className="text-xl font-semibold">
                    {fmtMoney(a.equity)}
                  </div>
                  <div className={`text-sm ${gainLoss(a.pnl_today)}`}>
                    {fmtMoney(a.pnl_today)} ({fmtPct(a.pnl_today_pct)})
                  </div>
                  <div className="mt-2 text-xs text-muted flex gap-3">
                    <span>{a.nb_positions} pos.</span>
                    <span>{a.nb_ordres_du_jour} ordres aujourd'hui</span>
                  </div>
                </>
              )}
            </button>
          ))}
          {ov && ov.par_compte.length === 0 && (
            <div className="text-muted text-sm">
              Aucun compte. Ajoute-en un.
            </div>
          )}
        </div>
      </Card>

      <Card title="Performance comparée (base 100)">
        {compData.length > 0 ? (
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={compData}>
                <CartesianGrid stroke="#252b39" strokeDasharray="3 3" />
                <XAxis
                  dataKey="ts"
                  type="number"
                  domain={["dataMin", "dataMax"]}
                  tickFormatter={(v) =>
                    new Date(v as number).toLocaleDateString()
                  }
                  stroke="#8a93a6"
                  fontSize={11}
                />
                <YAxis
                  stroke="#8a93a6"
                  fontSize={11}
                  domain={["dataMin", "dataMax"]}
                  tickFormatter={(v) => `${(v as number).toFixed(1)}`}
                  width={45}
                />
                <Tooltip
                  contentStyle={{
                    background: "#141821",
                    border: "1px solid #252b39",
                    borderRadius: 8,
                  }}
                  labelFormatter={(v) =>
                    new Date(v as number).toLocaleString()
                  }
                  formatter={(v: number) => v.toFixed(2)}
                />
                <Legend />
                {seriesKeys.map((k, i) => (
                  <Line
                    key={k}
                    type="monotone"
                    dataKey={k}
                    stroke={PALETTE[i % PALETTE.length]}
                    dot={false}
                    strokeWidth={2}
                    isAnimationActive={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center text-muted text-sm">
            Pas encore de données historiques.
          </div>
        )}
      </Card>

      <Card title="Exposition agrégée par symbole">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-muted text-left">
                <th className="py-2">Symbole</th>
                <th className="py-2 text-right">Qty totale</th>
                <th className="py-2 text-right">Valeur totale</th>
                <th className="py-2 text-right">P&L latent</th>
                <th className="py-2 text-right">Comptes</th>
              </tr>
            </thead>
            <tbody>
              {(ov?.positions_agregees ?? []).map((p) => (
                <tr key={p.symbol} className="border-t border-border">
                  <td className="py-2 font-medium">{p.symbol}</td>
                  <td className="py-2 text-right">{fmtNum(p.total_qty, 4)}</td>
                  <td className="py-2 text-right">
                    {fmtMoney(p.total_market_value)}
                  </td>
                  <td
                    className={`py-2 text-right ${gainLoss(
                      p.total_unrealized_pl,
                    )}`}
                  >
                    {fmtMoney(p.total_unrealized_pl)}
                  </td>
                  <td className="py-2 text-right">{p.nb_accounts}</td>
                </tr>
              ))}
              {ov && ov.positions_agregees.length === 0 && (
                <tr>
                  <td className="py-3 text-muted" colSpan={5}>
                    Aucune exposition.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
