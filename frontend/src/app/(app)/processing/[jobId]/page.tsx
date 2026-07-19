"use client";
import { use, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle2, Loader2, Circle, AlertCircle, ChevronDown } from "lucide-react";
import { api } from "@/lib/api";
import type { Job } from "@/types/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

// Frontend polls getJob every 2s. The backend also exposes an SSE stream
// (jobEventsUrl) on a 10s cadence; 2s client polling is more responsive for
// short jobs and avoids EventSource lifecycle quirks behind forwarded URLs.
export default function ProcessingPage({ params }: { params: Promise<{ jobId: string }> }) {
  const { jobId } = use(params);
  const router = useRouter();
  const [job, setJob] = useState<Job | null>(null);
  const [showLog, setShowLog] = useState(false);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let live = true;
    async function poll() {
      try {
        const j = await api.getJob(jobId);
        if (!live) return;
        setJob(j);
        if (j.status === "ready" || j.status === "failed") {
          if (timer.current) clearInterval(timer.current);
          if (j.status === "ready" && j.pack_id) router.push(`/workspace/${j.pack_id}`);
        }
      } catch { /* transient — keep polling */ }
    }
    poll();
    timer.current = setInterval(poll, 2000);
    return () => { live = false; if (timer.current) clearInterval(timer.current); };
  }, [jobId, router]);

  if (!job) {
    return <div className="grid place-items-center py-20 text-sm text-muted-foreground">Loading…</div>;
  }

  const failed = job.status === "failed";
  const ready = job.status === "ready";

  return (
    <div className="mx-auto max-w-2xl">
      <div className="text-center">
        <div className="text-5xl font-semibold text-accent">{job.percent}%</div>
        <div className="mt-2 flex items-center justify-center gap-2 text-lg font-semibold text-foreground">
          {!failed && !ready && <Loader2 className="h-5 w-5 animate-spin text-accent" />}
          {failed ? "Analysis failed" : ready ? "Analysis ready" : "Analysing…"}
        </div>
        <p className="mt-1 text-sm text-muted-foreground">{job.title}</p>
      </div>

      <Card className="mt-8 p-5">
        <ul className="space-y-3">
          {job.steps.map((s, i) => (
            <li key={i} className="flex items-center gap-3 text-sm">
              {s.state === "done" ? <CheckCircle2 className="h-5 w-5 text-success" />
                : s.state === "active" ? <Loader2 className="h-5 w-5 animate-spin text-accent" />
                : <Circle className="h-5 w-5 text-muted-foreground/40" />}
              <span className={s.state === "done" ? "text-muted-foreground line-through" : "text-foreground"}>
                {s.name}
              </span>
            </li>
          ))}
        </ul>
      </Card>

      <Card className="mt-4 overflow-hidden">
        <button
          onClick={() => setShowLog(!showLog)}
          className="flex w-full items-center justify-between px-5 py-3 text-sm font-medium text-foreground"
        >
          Agentic log
          <ChevronDown className={`h-4 w-4 transition-transform ${showLog ? "rotate-180" : ""}`} />
        </button>
        {showLog && (
          <div className="border-t border-border bg-muted/30 px-5 py-3 font-mono text-xs text-muted-foreground">
            {job.log.map((l, i) => (
              <div key={i}>{new Date(l.ts).toLocaleTimeString()} — {l.message}</div>
            ))}
          </div>
        )}
      </Card>

      {failed && (
        <Card className="mt-4 border-danger/30 bg-danger/[0.03] p-4">
          <div className="flex items-center gap-2 text-danger">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm font-semibold">Something went wrong</span>
          </div>
          <p className="mt-1 break-all text-xs text-muted-foreground">{job.error}</p>
          <Button variant="secondary" size="sm" className="mt-3" onClick={() => router.push("/new")}>
            Try again
          </Button>
        </Card>
      )}

      {ready && !job.pack_id && (
        <Card className="mt-4 p-4 text-center text-sm text-muted-foreground">
          Analysis complete. This was an ephemeral session, so it wasn&apos;t saved to your library.
        </Card>
      )}

      {!failed && !ready && (
        <div className="mt-6 rounded-sm bg-muted/50 px-4 py-3 text-center text-xs text-muted-foreground">
          You can leave this running — it continues in the background.
        </div>
      )}
    </div>
  );
}