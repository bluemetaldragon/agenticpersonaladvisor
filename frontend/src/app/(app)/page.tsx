"use client";
import { useState } from "react";
import { cn } from "@/lib/cn";
import ProfileLensesTab from "@/components/settings/profile-lenses";
import BrandingTab from "@/components/settings/branding";

const TABS = [
  { id: "profile", label: "Profile & Lenses" },
  { id: "branding", label: "Branding" },
];

export default function SettingsPage() {
  const [tab, setTab] = useState("profile");
  return (
    <div className="max-w-4xl">
      <p className="text-xs font-semibold uppercase tracking-wide text-accent">Preferences</p>
      <h1 className="mt-1 text-3xl font-semibold text-foreground">Account settings</h1>
      <p className="mt-1 text-sm text-muted-foreground">Configure your lenses and visual identity.</p>

      <div className="mt-6 flex w-fit gap-1 rounded-sm border border-border bg-card p-1">
        {TABS.map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={cn("rounded-[3px] px-4 py-2 text-sm font-medium transition-colors",
              tab === t.id ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:text-foreground")}>
            {t.label}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {tab === "profile" && <ProfileLensesTab />}
        {tab === "branding" && <BrandingTab />}
      </div>
    </div>
  );
}