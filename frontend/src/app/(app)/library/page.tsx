"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Search, ExternalLink, Trash2 } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { PackSummary } from "@/types/api";
import { Badge } from "@/components/ui/badge";

export default function LibraryPage() {
  const [packs, setPacks] = useState<PackSummary[]>([]);
  const [q, setQ] = useState("");
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { load(); }, []);
  function load() { api.listPacks().then(setPacks).catch(() => {}); }

  async function del(id: string) {
    try {
      await api.deletePack(id);
      setConfirmId(null);
      load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Delete failed.");
    }
  }

  const filtered = packs.filter((p) => p.title.toLowerCase().includes(q.toLowerCase()));

  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-accent">Repository</p>
      <h1 className="mt-1 text-3xl font-semibold text-foreground">Document library</h1>
      <p className="mt-1 text-sm text-muted-foreground">Your persisted board packs and their analyses.</p>

      <div className="mt-6 flex items-center gap-2 rounded-sm border border-border bg-card px-3 py-2">
        <Search className="h-4 w-4 text-muted-foreground" />
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search pack titles…"
          className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none" />
      </div>

      {error && <p className="mt-3 text-sm text-danger">{error}</p>}

      <div className="mt-4 overflow-hidden rounded-sm border border-border">
        <table className="w-full text-sm">
          <thead className="bg-muted/50 text-xs uppercase tracking-wide text-muted-foreground">
            <tr>
              <th className="px-4 py-3 text-left font-semibold">Pack title</th>
              <th className="px-4 py-3 text-left font-semibold">Date</th>
              <th className="px-4 py-3 text-left font-semibold">Retention</th>
              <th className="px-4 py-3 text-right font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr><td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">
                {packs.length === 0 ? "No packs yet." : "No matches."}
              </td></tr>
            ) : filtered.map((p) => (
              <tr key={p.pack_id} className="border-t border-border">
                <td className="px-4 py-3 font-medium text-foreground">{p.title}</td>
                <td className="px-4 py-3 text-muted-foreground">{new Date(p.uploaded_at).toLocaleDateString()}</td>
                <td className="px-4 py-3">
                  <Badge tone={p.retention_mode === "persist" ? "success" : "neutral"}>
                    {p.retention_mode === "persist" ? "Persisted" : "Ephemeral"}
                  </Badge>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center justify-end gap-2">
                    {confirmId === p.pack_id ? (
                      <>
                        <span className="text-xs text-muted-foreground">Delete permanently?</span>
                        <button onClick={() => del(p.pack_id)} className="text-xs font-semibold text-danger">Confirm</button>
                        <button onClick={() => setConfirmId(null)} className="text-xs text-muted-foreground">Cancel</button>
                      </>
                    ) : (
                      <>
                        <Link href={`/workspace/${p.pack_id}`} className="inline-flex items-center gap-1 rounded-sm border border-border px-2.5 py-1 text-xs text-foreground hover:bg-muted">
                          <ExternalLink className="h-3 w-3" /> Open
                        </Link>
                        <button aria-label="Delete pack" onClick={() => setConfirmId(p.pack_id)} className="rounded-sm p-1.5 text-muted-foreground hover:text-danger">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}