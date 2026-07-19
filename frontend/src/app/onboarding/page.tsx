"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  LayoutGrid, Upload, Cpu, MessageSquare, ShieldCheck, ArrowRight, Lock,
} from "lucide-react";
import { api } from "@/lib/api";
import { useSettings } from "@/components/theme-provider";
import { ONBOARDING_VERSION } from "@/lib/onboarding";
import { cn } from "@/lib/cn";

export default function OnboardingPage() {
  const router = useRouter();
  const { refresh } = useSettings();
  const [step, setStep] = useState(0);

  async function finish() {
    try {
      await api.updateSettings({ onboarding_seen_version: ONBOARDING_VERSION });
      refresh();
    } catch { /* proceed regardless */ }
    router.replace("/");
  }

  const next = () => (step < 2 ? setStep(step + 1) : finish());

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <div className="flex items-center justify-between px-8 py-6">
        <div className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-sm bg-accent text-accent-foreground">
            <LayoutGrid className="h-4 w-4" />
          </span>
          <span className="text-sm font-semibold text-foreground">Board Prep</span>
        </div>
        <button onClick={finish} className="text-sm font-medium text-muted-foreground hover:text-foreground">
          Skip
        </button>
      </div>

      <div className="mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center px-8 py-10">
        {step === 0 && (
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-accent">Welcome</p>
            <h1 className="mt-3 text-4xl font-semibold leading-tight text-foreground">
              A strategic, secure<br />board-preparation platform.
            </h1>
            <p className="mt-4 max-w-lg text-base text-muted-foreground">
              Engineered for bank non-executive directors. Turn a dense board pack into a
              personalised pre-read, sharp challenge questions, and sourced market context —
              shaped by your committee lens.
            </p>
          </div>
        )}

        {step === 1 && (
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-accent">How it works</p>
            <h1 className="mt-3 text-4xl font-semibold leading-tight text-foreground">
              From documents to<br />strategic clarity.
            </h1>
            <div className="mt-8 space-y-5">
              {[
                { icon: Upload, t: "Upload", d: "Securely upload your board pack as a PDF." },
                { icon: Cpu, t: "Analyse", d: "The engine drafts a pre-read and challenge sheet, shaped by your committee lens." },
                { icon: MessageSquare, t: "Deep-dive", d: "Interrogate any point with sourced external market analysis." },
              ].map((s, i) => (
                <div key={i} className="flex items-start gap-4">
                  <span className="grid h-10 w-10 shrink-0 place-items-center rounded-sm bg-accent/10 text-accent">
                    <s.icon className="h-5 w-5" />
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-foreground">{s.t}</p>
                    <p className="mt-0.5 text-sm text-muted-foreground">{s.d}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-accent">
              <Lock className="h-3.5 w-3.5" /> Privacy &amp; security
            </p>
            <h1 className="mt-3 text-4xl font-semibold leading-tight text-foreground">
              Your board pack never<br />leaves the confidential zone.
            </h1>
            <div className="mt-8 space-y-4">
              {[
                "Pack content, embeddings, and vectors stay inside the confidential zone.",
                "External research only ever receives a sanitised query — never your figures or text.",
                "Every external query is logged for audit, so the boundary is provable, not just asserted.",
              ].map((t, i) => (
                <div key={i} className="flex items-start gap-3">
                  <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                  <p className="text-sm text-foreground">{t}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between px-8 py-8">
        <div className="flex items-center gap-2">
          {[0, 1, 2].map((i) => (
            <span key={i} className={cn("h-1.5 rounded-full transition-all",
              i === step ? "w-8 bg-accent" : "w-2 bg-muted")} />
          ))}
          <span className="ml-3 text-xs text-muted-foreground">Step {step + 1} of 3</span>
        </div>
        <button onClick={next}
          className="inline-flex items-center gap-2 rounded-sm bg-accent px-5 py-2.5 text-sm font-medium text-accent-foreground hover:opacity-90">
          {step < 2 ? "Next" : "Enter the app"}
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}