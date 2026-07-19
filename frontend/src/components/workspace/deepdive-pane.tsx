"use client";
import { useState } from "react";
import { Search, Send } from "lucide-react";
import type { DeepDive } from "@/types/api";
import { DeepDiveCard } from "./deepdive-card";

export function DeepDivePane({
  deepdives, pending, onAsk,
}: {
  deepdives: DeepDive[];
  pending: boolean;
  onAsk: (question: string) => void;
}) {
  const [q, setQ] = useState("");
  const submit = () => {
    const text = q.trim();
    if (!text) return;
    onAsk(text);
    setQ("");
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto px-6 py-6">
        {deepdives.length === 0 ? (
          <div className="mx-auto mt-20 max-w-md text-center">
            <span className="mx-auto grid h-12 w-12 place-items-center rounded-[var(--radius-pill)] bg-muted text-muted-foreground">
              <Search className="h-5 w-5" />
            </span>
            <h2 className="mt-4 text-lg font-semibold text-foreground">Analysis workspace</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Ask about the pack, or launch a deep-dive from a pre-read or challenge item.
              Answers draw on external market research, sanitised at the query boundary.
            </p>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl space-y-6">
            {deepdives.map((dd) => (
              <div key={dd.id}>
                <div className="mb-2 flex justify-end">
                  <div className="max-w-[80%] rounded-sm bg-muted px-3 py-2 text-sm text-foreground">
                    {dd.question}
                  </div>
                </div>
                <DeepDiveCard dd={dd} />
              </div>
            ))}
            {pending && (
              <p className="text-center text-sm text-muted-foreground">Running deep-dive…</p>
            )}
          </div>
        )}
      </div>

      <div className="border-t border-border p-4">
        <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-sm border border-border bg-card p-2">
          <textarea
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } }}
            rows={1}
            placeholder="Ask a question about the board documentation…"
            className="flex-1 resize-none bg-transparent px-2 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
          />
          <button
            onClick={submit}
            disabled={!q.trim() || pending}
            className="grid h-9 w-9 place-items-center rounded-sm bg-accent text-accent-foreground disabled:opacity-40"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
        <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-muted-foreground">
          Answers draw on external market research, sanitised at the query boundary.
        </p>
      </div>
    </div>
  );
}
