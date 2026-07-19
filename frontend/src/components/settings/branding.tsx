"use client";
import { useEffect, useState } from "react";
import { Check } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { useSettings } from "@/components/theme-provider";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/cn";

const PALETTE = [
  { name: "Navy", hex: "#003366" },
  { name: "Slate", hex: "#334155" },
  { name: "Teal", hex: "#0f766e" },
  { name: "Indigo", hex: "#3730a3" },
  { name: "Forest", hex: "#14532d" },
  { name: "Burgundy", hex: "#7f1d1d" },
];

export default function BrandingTab() {
  const { settings, applyAccent, refresh } = useSettings();
  const [accent, setAccent] = useState("#003366");
  const [appName, setAppName] = useState("Board Preparation Dashboard");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (settings) {
      setAccent(settings.accent || "#003366");
      setAppName(settings.app_name || "Board Preparation Dashboard");
    }
  }, [settings]);

  function preview(hex: string) {
    setAccent(hex);
    setSaved(false);
    applyAccent(hex);
  }

  async function save() {
    setSaving(true); setError(null);
    try {
      await api.updateSettings({ accent, app_name: appName });
      refresh();
      setSaved(true);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Save failed.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-sm font-semibold text-foreground">Accent colour</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Repaints the app in real time. Doubles as a white-label lever for demos.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          {PALETTE.map((c) => (
            <button key={c.hex} onClick={() => preview(c.hex)}
              aria-label={c.name}
              className={cn("grid h-10 w-10 place-items-center rounded-sm border-2 transition-transform hover:scale-105",
                accent.toLowerCase() === c.hex.toLowerCase() ? "border-foreground" : "border-transparent")}
              style={{ background: c.hex }}>
              {accent.toLowerCase() === c.hex.toLowerCase() && <Check className="h-4 w-4 text-white" />}
            </button>
          ))}
          <label className="flex items-center gap-2 rounded-sm border border-border bg-card px-3">
            <span className="text-xs text-muted-foreground">Custom</span>
            <input type="color" value={accent} onChange={(e) => preview(e.target.value)}
              className="h-6 w-8 cursor-pointer border-0 bg-transparent p-0" />
          </label>
        </div>
      </div>

      <div>
        <h2 className="text-sm font-semibold text-foreground">Application name</h2>
        <input value={appName} onChange={(e) => { setAppName(e.target.value); setSaved(false); }}
          className="mt-3 w-full max-w-md rounded-sm border border-border bg-card px-3 py-2 text-sm text-foreground focus:outline-none" />
      </div>

      <Card className="p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Preview</p>
        <div className="mt-3 flex items-center gap-3">
          <span className="grid h-8 w-8 place-items-center rounded-sm bg-accent text-accent-foreground text-xs font-bold">B</span>
          <span className="text-sm font-semibold text-foreground">{appName}</span>
          <button className="ml-auto rounded-sm bg-accent px-3 py-1.5 text-xs font-medium text-accent-foreground">Primary action</button>
        </div>
      </Card>

      {error && <p className="text-sm text-danger">{error}</p>}
      <div className="flex items-center gap-3">
        <Button onClick={save} disabled={saving}>{saving ? "Saving…" : "Save branding"}</Button>
        {saved && <span className="inline-flex items-center gap-1 text-sm text-success"><Check className="h-4 w-4" /> Saved</span>}
      </div>
    </div>
  );
}