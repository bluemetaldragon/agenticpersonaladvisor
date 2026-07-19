"use client";
import Link from "next/link";
import { History } from "lucide-react";
import { cn } from "@/lib/cn";
import { Badge } from "@/components/ui/badge";
import type { Lens, RetentionMode } from "@/types/api";

export type Pane = "brief" | "deepdive";

export function WorkspaceTopbar({
  title, lenses, lensId, onLensChange, retention, pane, onPaneChange,
}: {
  title: string;
  lenses: Lens[];
  lensId: string;
  onLensChange: (id: string) => void;
  retention: RetentionMode;
  pane: Pane;
  onPaneChange: (p: Pane) => void;
}) {
  return (
    <header className="flex items-center gap-4 border-b border-border bg-background px-5 py-3">
      <Link href="/library" className="text-muted-foreground hover:text-foreground">
        <History className="h-4 w-4" />
      </Link>
      <h1 className="max-w-[240px] truncate text-sm font-semibold text-foreground">{title}</h1>

      <label className="flex items-center gap-2 rounded-sm border border-border bg-card px-3 py-1.5">
        <span className="text-xs text-muted-foreground">Lens:</span>
        <select
          value={lensId}
          onChange={(e) => onLensChange(e.target.value)}
          className="bg-transparent text-sm text-foreground focus:outline-none"
        >
          {lenses.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
        </select>
      </label>

      <Badge tone={retention === "persist" ? "success" : "neutral"}>
        {retention === "persist" ? "Persisted" : "Ephemeral"}
      </Badge>

      <div className="ml-auto flex rounded-sm border border-border bg-card p-0.5">
        {(["brief", "deepdive"] as const).map((p) => (
          <button
            key={p}
            onClick={() => onPaneChange(p)}
            className={cn(
              "rounded-[3px] px-4 py-1.5 text-sm font-medium transition-colors",
              pane === p ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:text-foreground",
            )}
          >
            {p === "brief" ? "Brief" : "Deep-dive"}
          </button>
        ))}
      </div>
    </header>
  );
}
