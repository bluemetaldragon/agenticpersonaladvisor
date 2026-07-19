"use client";
import { use, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { DeepDive, Lens, PackDetail } from "@/types/api";
import { WorkspaceTopbar, type Pane } from "@/components/workspace/workspace-topbar";
import { BriefPane } from "@/components/workspace/brief-pane";
import { DeepDivePane } from "@/components/workspace/deepdive-pane";

export default function WorkspacePage({ params }: { params: Promise<{ packId: string }> }) {
  const { packId } = use(params);
  const [detail, setDetail] = useState<PackDetail | null>(null);
  const [lenses, setLenses] = useState<Lens[]>([]);
  const [deepdives, setDeepdives] = useState<DeepDive[]>([]);
  const [pane, setPane] = useState<Pane>("brief");
  const [lensId, setLensId] = useState<string>("lens_fullboard");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const [d, ls] = await Promise.all([api.getPack(packId), api.listLenses()]);
        if (!live) return;
        setDetail(d);
        setLenses(ls);
        setDeepdives(d.deepdives);
      } catch (e) {
        if (live) setError(e instanceof ApiError ? e.message : "Failed to load pack.");
      }
    })();
    return () => { live = false; };
  }, [packId]);

  async function ask(question: string, sourceItemRef?: string) {
    setPending(true);
    setPane("deepdive");
    try {
      const dd = await api.createDeepDive(packId, question, sourceItemRef);
      setDeepdives((prev) => [...prev, dd]);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Deep-dive failed.");
    } finally {
      setPending(false);
    }
  }

  if (error) {
    return <div className="grid h-screen place-items-center bg-background text-sm text-danger">{error}</div>;
  }
  if (!detail) {
    return <div className="grid h-screen place-items-center bg-background text-sm text-muted-foreground">Loading…</div>;
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      <WorkspaceTopbar
        title={detail.pack.title}
        lenses={lenses}
        lensId={lensId}
        onLensChange={setLensId}
        retention={detail.pack.retention_mode}
        pane={pane}
        onPaneChange={setPane}
      />
      <div className="grid flex-1 overflow-hidden" style={{ gridTemplateColumns: pane === "brief" ? "minmax(340px, 420px) 1fr" : "0 1fr" }}>
        <div className={pane === "brief" ? "block overflow-hidden" : "hidden"}>
          <BriefPane
            preRead={detail.pre_read}
            challenge={detail.challenge}
            onDeepDive={(q, ref) => ask(q, ref)}
          />
        </div>
        <DeepDivePane deepdives={deepdives} pending={pending} onAsk={(q) => ask(q)} />
      </div>
    </div>
  );
}