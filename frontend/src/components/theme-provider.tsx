"use client";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { UserSettings } from "@/types/api";

type Ctx = {
  settings: UserSettings | null;
  applyAccent: (hex: string) => void;
  refresh: () => void;
};
const SettingsContext = createContext<Ctx>({ settings: null, applyAccent: () => {}, refresh: () => {} });
export const useSettings = () => useContext(SettingsContext);

function foregroundFor(hex: string): string {
  const h = hex.replace("#", "");
  if (h.length < 6) return "#f6f7f9";
  const r = parseInt(h.slice(0, 2), 16), g = parseInt(h.slice(2, 4), 16), b = parseInt(h.slice(4, 6), 16);
  const lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return lum > 0.6 ? "#1d1f23" : "#f6f7f9";
}

export function applyAccentToDom(hex: string) {
  const root = document.documentElement;
  root.style.setProperty("--accent", hex);
  root.style.setProperty("--accent-foreground", foregroundFor(hex));
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<UserSettings | null>(null);

  const refresh = useCallback(() => {
    api.getSettings().then((s) => {
      setSettings(s);
      if (s.accent) applyAccentToDom(s.accent);
      if (s.app_name) document.title = s.app_name;
    }).catch(() => {});
  }, []);

  useEffect(() => { refresh(); }, [refresh]);
  const applyAccent = useCallback((hex: string) => applyAccentToDom(hex), []);

  return (
    <SettingsContext.Provider value={{ settings, applyAccent, refresh }}>
      {children}
    </SettingsContext.Provider>
  );
}