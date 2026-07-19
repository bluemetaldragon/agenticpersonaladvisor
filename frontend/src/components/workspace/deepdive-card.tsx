"use client";
import { Maximize2, Copy, Pin, MessageSquarePlus, CornerUpLeft, AlertCircle } from "lucide-react";
import type { DeepDive } from "@/types/api";
import { Card } from "@/components/ui/card";
import { SanitisedQuery } from "./sanitised-query";
import { SourceChip } from "./source-chip";

// A deep-dive is "unverifiable" when synthesis found no external sources to ground it (FR-DD-6).
function isUnverifiable(dd: DeepDive): boolean {
  return dd.sources.length === 0;
}

export function DeepDiveCard({ dd }: { dd: DeepDive }) {
  const unverifiable = isUnverifiable(dd);

  return (
    <Card className={unverifiable ? "border-danger/30 bg-danger/[0.03] p-5" : "p-5"}>
      {dd.source_item_ref && (
        <div className="mb-3 inline-flex items-center gap-1.5 rounded-sm bg-muted px-2 py-1 text-xs text-muted-foreground">
          <CornerUpLeft className="h-3 w-3" />
          Launched from {dd.source_item_ref}
        </div>
      )}

      {unverifiable ? (
        <div>
          <div className="flex items-center gap-2 text-danger">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm font-semibold">Verification unavailable</span>
          </div>
          <p className="mt-2 text-sm leading-relaxed text-foreground">{dd.analysis}</p>
        </div>
      ) : (
        <>
          <p className="whitespace-pre-line text-sm leading-relaxed text-foreground">{dd.analysis}</p>

          {dd.sources.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {dd.sources.map((s, i) => <SourceChip key={i} source={s} />)}
            </div>
          )}

          <div className="mt-3">
            <SanitisedQuery query={dd.sanitised_query} />
          </div>

          <div className="mt-4 flex items-center justify-between border-t border-border pt-3">
            <div className="flex items-center gap-1">
              {[Maximize2, Copy, Pin].map((Icon, i) => (
                <button key={i} className="rounded-sm p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground">
                  <Icon className="h-4 w-4" />
                </button>
              ))}
            </div>
            <button className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground">
              <MessageSquarePlus className="h-4 w-4" /> Follow-up
            </button>
          </div>
        </>
      )}
    </Card>
  );
}
