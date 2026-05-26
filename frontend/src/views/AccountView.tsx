import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import { Card, LiveDot, Stat } from "../components/Layout";
import { EquityChart } from "../components/EquityChart";
import { fmtDate, fmtMoney, fmtNum, fmtPct, gainLoss } from "../format";
import { useState } from "react";

const REFETCH = 5000;

export function AccountView({ accountId }: { accountId: string }) {
  const [period, setPeriod] = useState("1M");

  const summaryQ = useQuery({
    queryKey: ["summary", accountId],
    queryFn: () => api.summary(accountId),
    refetchInterval: REFETCH,
  });
  const positionsQ = useQuery({
    queryKey: ["positions", accountId],
    queryFn: () => api.positions(accountId),
    refetchInterval: REFETCH,
  });
  const ordersQ = useQuery({
    queryKey: ["orders", accountId],
    queryFn: () => api.orders(accountId, 50),
    refetchInterval: REFETCH,
  });
  const historyQ = useQuery({
    queryKey: ["history", accountId, period],
    queryFn: () => api.history(accountId, period),
    refetchInterval: period === "1D" ? REFETCH : 60_000,
  });

  const s = summaryQ.data;
  return (
    <div className="flex flex-col gap-4">
      <Card right={<LiveDot />}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <Stat
            label="Equity"
            value={s ? fmtMoney(s.equity, s.currency) : "—"}
          />
          <Stat label="Cash" value={s ? fmtMoney(s.cash, s.currency) : "—"} />
          <Stat
            label="P&L du jour"
            value={s ? fmtMoney(s.pnl_today, s.currency) : "—"}
            sub={s ? fmtPct(s.pnl_today_pct) : undefined}
            tone={s ? (s.pnl_today >= 0 ? "gain" : "loss") : "neutral"}
          />
          <Stat
            label="P&L total"
            value={s ? fmtMoney(s.pnl_total, s.currency) : "—"}
            sub={s ? fmtPct(s.pnl_total_pct) : undefined}
            tone={s ? (s.pnl_total >= 0 ? "gain" : "loss") : "neutral"}
          />
        </div>
      </Card>

      <Card
        title="Equity"
        right={
          <div className="flex gap-1">
            {["1D", "1W", "1M", "3M", "1Y"].map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-2 py-1 text-xs rounded ${
                  period === p
                    ? "bg-accent/20 text-accent"
                    : "text-muted hover:text-text"
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        }
      >
        {historyQ.data && historyQ.data.points.length > 0 ? (
          <EquityChart points={historyQ.data.points} />
        ) : (
          <div className="h-64 flex items-center justify-center text-muted text-sm">
            {historyQ.isLoading ? "Chargement..." : "Pas de données."}
          </div>
        )}
      </Card>

      <Card title="Positions ouvertes">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-muted text-left">
                <Th>Symbole</Th>
                <Th>Côté</Th>
                <Th right>Qty</Th>
                <Th right>Prix entrée</Th>
                <Th right>Prix actuel</Th>
                <Th right>Valeur</Th>
                <Th right>P&L</Th>
                <Th right>%</Th>
              </tr>
            </thead>
            <tbody>
              {(positionsQ.data ?? []).map((p) => (
                <tr key={p.symbol} className="border-t border-border">
                  <Td className="font-medium">{p.symbol}</Td>
                  <Td className="capitalize">{p.side}</Td>
                  <Td right>{fmtNum(p.qty, 4)}</Td>
                  <Td right>{fmtMoney(p.avg_entry_price)}</Td>
                  <Td right>{fmtMoney(p.current_price)}</Td>
                  <Td right>{fmtMoney(p.market_value)}</Td>
                  <Td right className={gainLoss(p.unrealized_pl)}>
                    {fmtMoney(p.unrealized_pl)}
                  </Td>
                  <Td right className={gainLoss(p.unrealized_plpc)}>
                    {fmtPct(p.unrealized_plpc)}
                  </Td>
                </tr>
              ))}
              {positionsQ.data && positionsQ.data.length === 0 && (
                <tr>
                  <td className="py-3 text-muted" colSpan={8}>
                    Aucune position ouverte.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="Dernières actions des agents">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-muted text-left">
                <Th>Heure</Th>
                <Th>Agent</Th>
                <Th>Symbole</Th>
                <Th>Sens</Th>
                <Th right>Qty</Th>
                <Th>Type</Th>
                <Th>Statut</Th>
                <Th right>Prix exec.</Th>
              </tr>
            </thead>
            <tbody>
              {(ordersQ.data ?? []).map((o) => (
                <tr key={o.id} className="border-t border-border">
                  <Td>{fmtDate(o.submitted_at)}</Td>
                  <Td className="text-accent">{o.agent ?? "—"}</Td>
                  <Td className="font-medium">{o.symbol}</Td>
                  <Td
                    className={
                      o.side === "buy" ? "text-gain" : "text-loss"
                    }
                  >
                    {o.side}
                  </Td>
                  <Td right>{fmtNum(o.qty, 4)}</Td>
                  <Td>{o.type}</Td>
                  <Td>
                    <StatusPill status={o.status} />
                  </Td>
                  <Td right>
                    {o.filled_avg_price ? fmtMoney(o.filled_avg_price) : "—"}
                  </Td>
                </tr>
              ))}
              {ordersQ.data && ordersQ.data.length === 0 && (
                <tr>
                  <td className="py-3 text-muted" colSpan={8}>
                    Aucun ordre récent.
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

function Th({
  children,
  right,
}: {
  children: React.ReactNode;
  right?: boolean;
}) {
  return (
    <th
      className={`py-2 text-xs uppercase font-medium ${
        right ? "text-right" : "text-left"
      }`}
    >
      {children}
    </th>
  );
}

function Td({
  children,
  right,
  className = "",
}: {
  children: React.ReactNode;
  right?: boolean;
  className?: string;
}) {
  return (
    <td className={`py-2 ${right ? "text-right" : ""} ${className}`}>
      {children}
    </td>
  );
}

function StatusPill({ status }: { status: string }) {
  const filled = status === "filled";
  const cancelled =
    status === "canceled" || status === "rejected" || status === "expired";
  const cls = filled
    ? "bg-gain/15 text-gain"
    : cancelled
    ? "bg-loss/15 text-loss"
    : "bg-muted/10 text-muted";
  return (
    <span className={`px-2 py-0.5 rounded text-xs ${cls}`}>{status}</span>
  );
}
