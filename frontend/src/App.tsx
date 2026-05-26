import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";
import { OverviewView } from "./views/OverviewView";
import { AccountView } from "./views/AccountView";
import { AddAccountModal } from "./components/AddAccountModal";

type Tab = { kind: "overview" } | { kind: "account"; id: string };

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
            {(accountsQ.data ?? []).map((a) => (
              <div key={a.id} className="flex items-center group">
                <TabBtn
                  active={tab.kind === "account" && tab.id === a.id}
                  onClick={() => setTab({ kind: "account", id: a.id })}
                >
                  {a.label}
                </TabBtn>
                <button
                  className="opacity-0 group-hover:opacity-100 text-muted hover:text-loss text-xs px-1"
                  title="Supprimer ce compte"
                  onClick={() => {
                    if (confirm(`Supprimer le compte "${a.label}" ?`)) {
                      delMut.mutate(a.id);
                    }
                  }}
                >
                  ✕
                </button>
              </div>
            ))}
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
      </main>

      {showAdd && <AddAccountModal onClose={() => setShowAdd(false)} />}
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
