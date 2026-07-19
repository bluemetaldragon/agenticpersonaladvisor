"use client";
import { useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";
import { api } from "@/lib/api";
import type { RunTrace, PackSummary } from "@/types/api";
import { Badge } from "@/components/ui/badge";

const RUN_LABEL: Record<string, string> = {
  ingest: "Ingest", preread: "Pre-read", challenge: "Challenge", deepdive: "Deep-dive",
};

export default function ActivityPage() {
  const [traces, setTraces] = useState<RunTrace[]>([]);
  const [packs, setPacks] = useState<Record<string, string>>({});

  useEffect(() => {
    api.listAllTraces().then(setTraces).catch(() => {});
    api.listPacks().then((ps: PackSummary[]) =>
      setPacks(Object.fromEntries(ps.map((p) => [p.pack_id, p.title])))
    ).catch(() => {});
  }, []);

  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-accent">Governance</p>
      <h1 className="mt-1 text-3xl font-semibold text-foreground">Activity</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Every agent run is traced. Deep-dive runs record the exact query sent to external
        research — the receipt that pack content never crossed the confidential boundary.
      </p>

      {traces.length === 0 ? (
        <p className="mt-8 text-sm text-muted-foreground">
          No runs recorded yet. Run a deep-dive to see its sanitised query logged here.
        </p>
      ) : (
        <div className="mt-6 space-y-2">
          {traces.map((t) => (
            <div key={t.id} className="rounded-sm border border-border bg-card p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge tone={t.run_type === "deepdive" ? "accent" : "neutral"}>
                    {RUN_LABEL[t.run_type] ?? t.run_type}
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    {packs[t.pack_id] ?? t.pack_id}
                  </span>
                </div>
                <span className="text-xs text-muted-foreground">
                  {new Date(t.created_at).toLocaleString()}
                </span>
              </div>
              {t.firewall_query && (
                <div className="mt-3 flex items-start gap-2 rounded-sm bg-success/5 px-3 py-2">
                  <ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0 text-success" />
                  <div>
                    <p className="text-xs font-medium text-success">Sanitised external query</p>
                    <p className="mt-0.5 font-mono text-xs text-foreground">&ldquo;{t.firewall_query}&rdquo;</p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}