export type Account = {
  id: string;
  label: string;
  base_url: string;
};

export type Summary = {
  equity: number;
  cash: number;
  buying_power: number;
  last_equity: number;
  pnl_today: number;
  pnl_today_pct: number;
  pnl_total: number;
  pnl_total_pct: number;
  status: string;
  currency: string;
};

export type Position = {
  symbol: string;
  qty: number;
  side: string;
  avg_entry_price: number;
  current_price: number;
  market_value: number;
  cost_basis: number;
  unrealized_pl: number;
  unrealized_plpc: number;
};

export type Order = {
  id: string;
  client_order_id: string | null;
  agent: string | null;
  submitted_at: string | null;
  filled_at: string | null;
  symbol: string;
  side: string;
  qty: number;
  filled_qty: number;
  type: string;
  status: string;
  filled_avg_price: number;
  limit_price: number;
};

export type HistoryPoint = { ts: number; equity: number; profit_loss: number };
export type History = { base_value: number; timeframe: string; points: HistoryPoint[] };

export type AccountOverview = {
  id: string;
  label: string;
  statut_connexion: "ok" | "erreur";
  error?: string;
  equity: number;
  cash?: number;
  pnl_today: number;
  pnl_today_pct: number;
  pnl_total: number;
  nb_positions: number;
  nb_ordres_du_jour: number;
};

export type AggregatedPosition = {
  symbol: string;
  total_qty: number;
  total_market_value: number;
  total_unrealized_pl: number;
  nb_accounts: number;
  accounts: { id: string; label: string; qty: number }[];
};

export type Overview = {
  total_equity: number;
  total_cash: number;
  total_pnl_today: number;
  total_pnl_today_pct: number;
  total_pnl_total: number;
  par_compte: AccountOverview[];
  positions_agregees: AggregatedPosition[];
};

// --- Analyse de graphiques (Pilier A — analyse technique) ---
export type AnalysisMetrics = {
  n_trades: number;
  taux_reussite?: number;
  rendement_moyen?: number;
  rendement_median?: number;
  rendement_total_cumule?: number;
  meilleur?: number;
  pire?: number;
  duree_moyenne_jours?: number;
};

export type AnalysisTrade = {
  entry_date: string;
  exit_date: string;
  entry_price: number;
  exit_price: number;
  return_pct: number;
  holding_days: number;
};

export type BuyHold = {
  start_date?: string;
  end_date?: string;
  start_price?: number;
  end_price?: number;
  total_return?: number;
  equity?: (number | null)[];
};

export type OpenPosition = {
  entry_date: string;
  entry_price: number;
  current_price: number;
  unrealized_return: number;
};

export type Overlay = {
  name: string;
  key: string;
  color: string;
  data: (number | null)[];
};

// Oscillateur (RSI…) : tracé dans un panneau séparé 0-100 avec ses seuils.
export type Oscillator = {
  name: string;
  data: (number | null)[];
  lower: number;
  upper: number;
};

export type StrategyResult = {
  key: string;
  label: string;
  color: string;
  metrics: AnalysisMetrics;
  strategy_total_with_open: number;
  open_position: OpenPosition | null;
  trades: AnalysisTrade[];
  equity: (number | null)[];
  overlays: Overlay[];
  oscillator: Oscillator | null;
};

export type Analysis = {
  ticker: string;
  short: number;
  long: number;
  dates: string[];
  close: (number | null)[];
  benchmark: BuyHold;
  strategies: StrategyResult[];
};

export type StrategyInfo = { key: string; label: string };

export type AnalysisDefaults = {
  tickers: string[];
  ma_short: number;
  ma_long: number;
  strategies: StrategyInfo[];
};

const BASE = "/api";

async function j<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!r.ok) {
    throw new Error(`${r.status} ${r.statusText}`);
  }
  if (r.status === 204) return undefined as T;
  return r.json();
}

export const api = {
  listAccounts: () => j<Account[]>("/accounts"),
  createAccount: (body: {
    label: string;
    api_key: string;
    api_secret: string;
    base_url?: string;
  }) => j<Account>("/accounts", { method: "POST", body: JSON.stringify(body) }),
  deleteAccount: (id: string) =>
    j<void>(`/accounts/${id}`, { method: "DELETE" }),
  summary: (id: string) => j<Summary>(`/accounts/${id}/summary`),
  positions: (id: string) => j<Position[]>(`/accounts/${id}/positions`),
  orders: (id: string, limit = 50) =>
    j<Order[]>(`/accounts/${id}/orders?limit=${limit}`),
  history: (id: string, period = "1M", timeframe?: string) =>
    j<History>(
      `/accounts/${id}/history?period=${encodeURIComponent(period)}${
        timeframe ? `&timeframe=${encodeURIComponent(timeframe)}` : ""
      }`,
    ),
  overview: () => j<Overview>("/overview"),
  analysisDefaults: () => j<AnalysisDefaults>("/analysis/defaults"),
  analyze: (ticker: string, short: number, long: number) =>
    j<Analysis>(
      `/analysis/${encodeURIComponent(ticker)}?short=${short}&long=${long}`,
    ),
};
