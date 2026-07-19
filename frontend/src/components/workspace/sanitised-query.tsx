"use client";
import { useState } from "react";
import { ShieldCheck, ChevronDown } from "lucide-react";
import { cn } from "@/lib/cn";

export function SanitisedQuery({ query }: { query?: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button
        onClick={() => setOpen((o) => !o)}
        className={cn(
          "inline-flex items-center gap-1.5 rounded-[var(--radius-pill)] px-2.5 py-1",
          "text-xs font-medium text-success bg-success/10 hover:bg-success/15 transition-colors",
        )}
        aria-expanded={open}
      >
        <ShieldCheck className="h-3.5 w-3.5" />
        Sanitised query
        <ChevronDown className={cn("h-3 w-3 transition-transform", open && "rotate-180")} />
      </button>
      {open && (
        <div className="mt-2 rounded-sm border border-border bg-muted/50 px-3 py-2">
          <p className="text-xs text-muted-foreground">
            Exact query sent to external research — no figures, no pack text:
          </p>
          <p className="mt-1 font-mono text-xs text-foreground">
            {query ? `"${query}"` : "—"}
          </p>
        </div>
      )}
    </div>
  );
}
