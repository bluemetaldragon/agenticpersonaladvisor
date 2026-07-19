"use client";
import { useEffect, useState } from "react";
import { Plus, Pencil, Trash2, X, Check } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { useSettings } from "@/components/theme-provider";
import type { Lens } from "@/types/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/cn";

const DEPTHS = ["brief", "standard", "deep"] as const;

export default function ProfileLensesTab() {
  const { settings, refresh } = useSettings();
  const [lenses, setLenses] = useState<Lens[]>([]);
  const [defaultLens, setDefaultLens] = useState("lens_fullboard");
  const [depth, setDepth] = useState<string>("standard");
  const [focus, setFocus] = useState<string[]>([]);
  const [focusInput, setFocusInput] = useState("");
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [editing, setEditing] = useState<Lens | null>(null);
  const [lensName, setLensName] = useState("");
  const [lensKeywords, setLensKeywords] = useState("");

  useEffect(() => { loadLenses(); }, []);
  useEffect(() => {
    if (settings) {
      setDefaultLens(settings.default_lens || "lens_fullboard");
      setDepth(settings.depth || "standard");
      setFocus(settings.focus_areas || []);
    }
  }, [settings]);

  function loadLenses() { api.listLenses().then(setLenses).catch(() => {}); }

  async function saveProfile() {
    setError(null);
    try {
      await api.updateSettings({ default_lens: defaultLens, depth, focus_areas: focus });
      refresh();
      setSaved(true);
    } catch (e) { setError(e instanceof ApiError ? e.message : "Save failed."); }
  }

  function addFocus() {
    const v = focusInput.trim();
    if (v && !focus.includes(v)) { setFocus([...focus, v]); setFocusInput(""); setSaved(false); }
  }

  function startCreate() { setEditing({ id: "", name: "", keywords: [], builtin: false }); setLensName(""); setLensKeywords(""); }
  function startEdit(l: Lens) { setEditing(l); setLensName(l.name); setLensKeywords(l.keywords.join(", ")); }

  async function saveLens() {
    const keywords = lensKeywords.split(",").map((k) => k.trim()).filter(Boolean);
    try {
      if (editing?.id) await api.updateLens(editing.id, { id: editing.id, name: lensName, keywords });
      else await api.createLens({ name: lensName, keywords });
      setEditing(null); loadLenses();
    } catch (e) { setError(e instanceof ApiError ? e.message : "Lens save failed."); }
  }

  async function deleteLens(id: string) {
    try { await api.deleteLens(id); loadLenses(); }
    catch (e) { setError(e instanceof ApiError ? e.message : "Delete failed."); }
  }

  const customLenses = lenses.filter((l) => !l.builtin);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-sm font-semibold text-foreground">Default strategic lens</h2>
        <p className="mt-1 text-sm text-muted-foreground">Pre-selected for new analyses. Overridable per session.</p>
        <div className="mt-3 flex flex-wrap items-center gap-4">
          <select value={defaultLens} onChange={(e) => { setDefaultLens(e.target.value); setSaved(false); }}
            className="rounded-sm border border-border bg-card px-3 py-2 text-sm text-foreground focus:outline-none">
            {lenses.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>
          <div className="flex rounded-sm border border-border bg-card p-0.5">
            {DEPTHS.map((d) => (
              <button key={d} onClick={() => { setDepth(d); setSaved(false); }}
                className={cn("rounded-[3px] px-3 py-1.5 text-sm capitalize transition-colors",
                  depth === d ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:text-foreground")}>
                {d}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-sm font-semibold text-foreground">Focus areas</h2>
        <p className="mt-1 text-sm text-muted-foreground">Keywords the analysis always prioritises.</p>
        <div className="mt-3 flex gap-2">
          <input value={focusInput} onChange={(e) => setFocusInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addFocus(); } }}
            placeholder="e.g. Liquidity, M&A"
            className="flex-1 max-w-md rounded-sm border border-border bg-card px-3 py-2 text-sm text-foreground focus:outline-none" />
          <Button variant="secondary" size="sm" onClick={addFocus}><Plus className="h-4 w-4" /></Button>
        </div>
        {focus.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {focus.map((f) => (
              <span key={f} className="inline-flex items-center gap-1.5 rounded-[var(--radius-pill)] bg-muted px-3 py-1 text-xs text-foreground">
                {f}
                <button onClick={() => { setFocus(focus.filter((x) => x !== f)); setSaved(false); }}><X className="h-3 w-3 text-muted-foreground" /></button>
              </span>
            ))}
          </div>
        )}
      </div>

      <div>
        <h2 className="text-sm font-semibold text-foreground">Custom lenses</h2>
        <p className="mt-1 text-sm text-muted-foreground">Specialised committee perspectives (name + focus keywords).</p>
        <div className="mt-3 space-y-2">
          {customLenses.map((l) => (
            <Card key={l.id} className="flex items-center justify-between p-3">
              <div>
                <p className="text-sm font-medium text-foreground">{l.name}</p>
                <p className="text-xs text-muted-foreground">{l.keywords.join(" · ")}</p>
              </div>
              <div className="flex gap-1">
                <button onClick={() => startEdit(l)} className="rounded-sm p-1.5 text-muted-foreground hover:bg-muted"><Pencil className="h-4 w-4" /></button>
                <button onClick={() => deleteLens(l.id)} className="rounded-sm p-1.5 text-muted-foreground hover:text-danger"><Trash2 className="h-4 w-4" /></button>
              </div>
            </Card>
          ))}

          {editing ? (
            <Card className="space-y-3 p-4">
              <input value={lensName} onChange={(e) => setLensName(e.target.value)} placeholder="Lens name"
                className="w-full rounded-sm border border-border bg-card px-3 py-2 text-sm focus:outline-none" />
              <input value={lensKeywords} onChange={(e) => setLensKeywords(e.target.value)} placeholder="keywords, comma, separated"
                className="w-full rounded-sm border border-border bg-card px-3 py-2 text-sm focus:outline-none" />
              <div className="flex gap-2">
                <Button size="sm" onClick={saveLens} disabled={!lensName.trim()}>Save lens</Button>
                <Button size="sm" variant="ghost" onClick={() => setEditing(null)}>Cancel</Button>
              </div>
            </Card>
          ) : (
            <button onClick={startCreate}
              className="flex w-full items-center justify-center gap-2 rounded-sm border border-dashed border-border py-3 text-sm text-muted-foreground hover:bg-muted">
              <Plus className="h-4 w-4" /> Create new lens
            </button>
          )}
        </div>
      </div>

      {error && <p className="text-sm text-danger">{error}</p>}
      <div className="flex items-center gap-3 border-t border-border pt-4">
        <Button onClick={saveProfile}>Save settings</Button>
        {saved && <span className="inline-flex items-center gap-1 text-sm text-success"><Check className="h-4 w-4" /> Saved</span>}
      </div>
    </div>
  );
}