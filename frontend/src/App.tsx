import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";
import { OverviewView } from "./views/OverviewView";
import { AccountView } from "./views/AccountView";
import { AnalysisView } from "./views/AnalysisView";
import { AssistantView } from "./views/AssistantView";
import { AddAccountModal } from "./components/AddAccountModal";

type Tab =
  | { kind: "overview" }
  | { kind: "account"; id: string }
  | { kind: "analysis" }
  | { kind: "assistant" };

export default function App() {
  const qc = useQueryClient();
  const accountsQ = useQuery({
    queryKey: ["accounts"],
    queryFn: () => api.listAccounts(),
    refetchInterval: 30_000,
  });
  const [tab, setTab] = useState<Tab>({ kind: "overview" });
  const [showAdd, setShowAdd] = useState(false);

  useEffect(() => {
    if (tab.kind === "account") {
      const exists = accountsQ.data?.some((a) => a.id === tab.id);
      if (accountsQ.data && !exists) setTab({ kind: "overview" });
    }
  }, [accountsQ.data, tab]);

  const delMut = useMutation({
    mutationFn: (id: string) => api.deleteAccount(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["accounts"] }),
  });

  return (
    <div className="min-h-full">
      <header className="border-b border-border bg-panel">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="w-2 h-6 bg-accent rounded" />
            <h1 className="font-semibold text-lg">TradingMonitor</h1>
            <span className="text-xs text-muted ml-2">paper · read-only</span>
          </div>
          <nav className="flex gap-1 items-center ml-4 flex-wrap">
            <TabBtn
              active={tab.kind === "overview"}
              onClick={() => setTab({ kind: "overview" })}
            >
              Vue d'ensemble
            </TabBtn>
            <TabBtn
              active={tab.kind === "analysis"}
              onClick={() => setTab({ kind: "analysis" })}
            >
              Analyse
            </TabBtn>
            <TabBtn
              active={tab.kind === "assistant"}
              onClick={() => setTab({ kind: "assistant" })}
            >
              Assistant
            </TabBtn>
            <AgentsDropdown
              accounts={accountsQ.data ?? []}
              activeId={tab.kind === "account" ? tab.id : null}
              onSelect={(id) => setTab({ kind: "account", id })}
              onDelete={(id, label) => {
                if (confirm(`Supprimer le compte "${label}" ?`)) {
                  delMut.mutate(id);
                }
              }}
            />
          </nav>
          <div className="ml-auto">
            <button
              className="text-sm px-3 py-1.5 bg-accent/15 text-accent rounded hover:bg-accent/25"
              onClick={() => setShowAdd(true)}
            >
              + Ajouter un compte
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {tab.kind === "analysis" ? (
          <AnalysisView />
        ) : tab.kind === "assistant" ? (
          <AssistantView />
        ) : (
        <>
        {accountsQ.isLoading && (
          <div className="text-muted">Chargement…</div>
        )}
        {accountsQ.isError && (
          <div className="text-loss">Backend injoignable. Lancé sur :8000 ?</div>
        )}
        {accountsQ.data && accountsQ.data.length === 0 && (
          <div className="bg-panel border border-border rounded-xl p-8 text-center">
            <p className="text-muted mb-4">
              Aucun compte configuré pour le moment.
            </p>
            <button
              className="text-sm px-3 py-1.5 bg-accent/15 text-accent rounded"
              onClick={() => setShowAdd(true)}
            >
              + Ajouter un compte paper
            </button>
          </div>
        )}
        {accountsQ.data && accountsQ.data.length > 0 && (
          <>
            {tab.kind === "overview" ? (
              <OverviewView
                onSelectAccount={(id) => setTab({ kind: "account", id })}
              />
            ) : (
              <AccountView accountId={tab.id} />
            )}
          </>
        )}
        </>
        )}
      </main>

      {showAdd && <AddAccountModal onClose={() => setShowAdd(false)} />}
    </div>
  );
}

function AgentsDropdown({
  accounts,
  activeId,
  onSelect,
  onDelete,
}: {
  accounts: { id: string; label: string }[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string, label: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  const active = accounts.find((a) => a.id === activeId);
  const isActive = activeId != null;

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((v) => !v)}
        className={`flex items-center gap-1.5 px-3 py-1.5 text-sm rounded ${
          isActive
            ? "bg-accent/15 text-accent"
            : "text-muted hover:text-text hover:bg-panel2"
        }`}
      >
        <span>
          {active ? active.label : "Agents"}
          {accounts.length > 0 && (
            <span className="ml-1.5 text-xs opacity-60">{accounts.length}</span>
          )}
        </span>
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          className={`transition-transform ${open ? "rotate-180" : ""}`}
        >
          <path d="M6 9l6 6 6-6" />
        </svg>
      </button>

      {open && (
        <div className="absolute left-0 mt-1 w-56 max-h-72 overflow-y-auto bg-panel border border-border rounded-lg shadow-xl z-20 py-1">
          {accounts.length === 0 ? (
            <div className="px-3 py-2 text-xs text-muted">Aucun agent</div>
          ) : (
            accounts.map((a) => (
              <div
                key={a.id}
                className="flex items-center group px-1"
              >
                <button
                  onClick={() => {
                    onSelect(a.id);
                    setOpen(false);
                  }}
                  className={`flex-1 text-left px-2 py-1.5 text-sm rounded ${
                    a.id === activeId
                      ? "bg-accent/15 text-accent"
                      : "text-text hover:bg-panel2"
                  }`}
                >
                  {a.label}
                </button>
                <button
                  className="opacity-0 group-hover:opacity-100 text-muted hover:text-loss text-xs px-2"
                  title="Supprimer ce compte"
                  onClick={() => onDelete(a.id, a.label)}
                >
                  ✕
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

function TabBtn({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 text-sm rounded ${
        active
          ? "bg-accent/15 text-accent"
          : "text-muted hover:text-text hover:bg-panel2"
      }`}
    >
      {children}
    </button>
  );
}
