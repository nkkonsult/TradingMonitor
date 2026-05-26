import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { HistoryPoint } from "../api";

export function EquityChart({ points }: { points: HistoryPoint[] }) {
  const data = points.map((p) => ({
    ts: p.ts * 1000,
    equity: p.equity,
  }));
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="eq" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#60a5fa" stopOpacity={0.5} />
              <stop offset="100%" stopColor="#60a5fa" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#252b39" strokeDasharray="3 3" />
          <XAxis
            dataKey="ts"
            type="number"
            domain={["dataMin", "dataMax"]}
            tickFormatter={(v) => new Date(v).toLocaleDateString()}
            stroke="#8a93a6"
            fontSize={11}
          />
          <YAxis
            stroke="#8a93a6"
            fontSize={11}
            domain={["dataMin", "dataMax"]}
            tickFormatter={(v) => `$${Math.round(v).toLocaleString()}`}
            width={80}
          />
          <Tooltip
            contentStyle={{
              background: "#141821",
              border: "1px solid #252b39",
              borderRadius: 8,
            }}
            labelFormatter={(v) => new Date(v as number).toLocaleString()}
            formatter={(v: number) => [`$${v.toFixed(2)}`, "Equity"]}
          />
          <Area
            type="monotone"
            dataKey="equity"
            stroke="#60a5fa"
            fill="url(#eq)"
            strokeWidth={2}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
