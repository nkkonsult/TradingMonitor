import { ReactNode } from "react";

export function LiveDot({ label = "live" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-xs text-muted">
      <span className="pulse-dot" />
      <span>{label}</span>
    </div>
  );
}

export function Card({
  title,
  right,
  children,
  className = "",
}: {
  title?: string;
  right?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`bg-panel border border-border rounded-xl p-4 ${className}`}
    >
      {(title || right) && (
        <div className="flex items-center justify-between mb-3">
          {title && (
            <h2 className="text-sm font-medium text-muted uppercase tracking-wide">
              {title}
            </h2>
          )}
          {right}
        </div>
      )}
      {children}
    </div>
  );
}

export function Stat({
  label,
  value,
  sub,
  tone = "neutral",
}: {
  label: string;
  value: string;
  sub?: string;
  tone?: "neutral" | "gain" | "loss";
}) {
  const toneCls =
    tone === "gain" ? "text-gain" : tone === "loss" ? "text-loss" : "text-text";
  return (
    <div className="flex flex-col">
      <div className="text-xs uppercase tracking-wide text-muted">{label}</div>
      <div className={`text-2xl font-semibold ${toneCls}`}>{value}</div>
      {sub && <div className={`text-sm ${toneCls} opacity-80`}>{sub}</div>}
    </div>
  );
}
