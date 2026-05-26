import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../api";

export function AddAccountModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [label, setLabel] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [baseUrl, setBaseUrl] = useState("https://paper-api.alpaca.markets");

  const m = useMutation({
    mutationFn: () =>
      api.createAccount({
        label,
        api_key: apiKey,
        api_secret: apiSecret,
        base_url: baseUrl,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accounts"] });
      onClose();
    },
  });

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-panel border border-border rounded-xl p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">Ajouter un compte paper</h3>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            m.mutate();
          }}
          className="flex flex-col gap-3"
        >
          <Field label="Label">
            <input
              required
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              className="input"
              placeholder="ex: Bot RSI"
            />
          </Field>
          <Field label="API Key">
            <input
              required
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="input"
              spellCheck={false}
            />
          </Field>
          <Field label="API Secret">
            <input
              required
              type="password"
              value={apiSecret}
              onChange={(e) => setApiSecret(e.target.value)}
              className="input"
              spellCheck={false}
            />
          </Field>
          <Field label="Base URL">
            <input
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              className="input"
            />
          </Field>
          {m.isError && (
            <div className="text-loss text-sm">
              {(m.error as Error).message}
            </div>
          )}
          <div className="flex justify-end gap-2 mt-2">
            <button
              type="button"
              className="btn-ghost"
              onClick={onClose}
              disabled={m.isPending}
            >
              Annuler
            </button>
            <button type="submit" className="btn" disabled={m.isPending}>
              {m.isPending ? "Ajout..." : "Ajouter"}
            </button>
          </div>
        </form>
        <style>{`
          .input { background:#0b0d12; border:1px solid #252b39; padding:8px 10px; border-radius:8px; color:#e6e9ef; font-size:14px; }
          .input:focus { outline:none; border-color:#60a5fa; }
          .btn { background:#60a5fa; color:#0b0d12; font-weight:600; padding:8px 14px; border-radius:8px; }
          .btn:disabled { opacity:.5; }
          .btn-ghost { color:#8a93a6; padding:8px 14px; border-radius:8px; }
          .btn-ghost:hover { color:#e6e9ef; }
        `}</style>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-xs uppercase tracking-wide text-muted">{label}</span>
      {children}
    </label>
  );
}
