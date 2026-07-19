"use client";
import { Search } from "lucide-react";
import type { PreRead, ChallengeSheet } from "@/types/api";

export function BriefPane({
  preRead, challenge, onDeepDive,
}: {
  preRead: PreRead | null;
  challenge: ChallengeSheet | null;
  onDeepDive: (question: string, sourceItemRef: string) => void;
}) {
  return (
    <div className="flex h-full flex-col overflow-y-auto border-r border-border">
      <section className="px-5 pt-5">
        <div className="flex items-center justify-between pb-3">
          <h2 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Strategic pre-reads
          </h2>
          <span className="rounded-[var(--radius-pill)] bg-muted px-2 py-0.5 text-xs text-muted-foreground">
            {preRead?.items.length ?? 0}
          </span>
        </div>

        <ul className="space-y-3">
          {preRead?.items.map((item) => (
            <li key={item.item_ref} className="rounded-sm border border-border bg-card p-4">
              <div className="flex items-start justify-between gap-2">
                <h3 className="text-sm font-semibold text-foreground">{item.heading}</h3>
                <span className="shrink-0 rounded-[var(--radius-pill)] bg-muted px-2 py-0.5 text-[11px] text-muted-foreground">
                  {item.source_section_ref}
                </span>
              </div>
              <p className="mt-1.5 line-clamp-3 text-sm leading-relaxed text-muted-foreground">
                {item.body}
              </p>
              <button
                onClick={() => onDeepDive(`Provide external context on: ${item.heading}`, item.item_ref)}
                className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-accent hover:opacity-80"
              >
                <Search className="h-3.5 w-3.5" /> Deep-dive
              </button>
            </li>
          ))}
          {!preRead && <p className="text-sm text-muted-foreground">Pre-read not available.</p>}
        </ul>
      </section>

      <section className="px-5 py-6">
        <h2 className="pb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Challenge questions
        </h2>
        <ul className="space-y-3">
          {challenge?.items.map((item) => (
            <li key={item.item_ref} className="rounded-sm border border-border bg-card p-4">
              <p className="text-sm text-foreground">{item.question}</p>
              <div className="mt-2 flex items-center justify-between">
                <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                  ↳ links to {item.source_item_ref}
                </span>
                <button
                  onClick={() => onDeepDive(item.question, item.source_item_ref)}
                  className="text-xs font-semibold uppercase tracking-wide text-accent hover:opacity-80"
                >
                  Deep-dive
                </button>
              </div>
            </li>
          ))}
          {!challenge && <p className="text-sm text-muted-foreground">Challenge sheet not generated yet.</p>}
        </ul>
      </section>
    </div>
  );
}
