"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Upload, FileText, Shield } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { Lens, RetentionMode } from "@/types/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function NewPackPage() {
  const router = useRouter();
  const [lenses, setLenses] = useState<Lens[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [lensId, setLensId] = useState("lens_fullboard");
  const [retention, setRetention] = useState<RetentionMode>("persist");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    api.listLenses().then(setLenses).catch(() => {});
  }, []);

  function pick(f: File | null) {
    if (!f) return;
    if (f.type !== "application/pdf") { setError("Please select a PDF file."); return; }
    setError(null);
    setFile(f);
    if (!title) setTitle(f.name.replace(/\.pdf$/i, ""));
  }

  async function start() {
    if (!file) return;
    setSubmitting(true);
    setError(null);
    try {
      const { job_id } = await api.uploadPack(file, {
        title: title || file.name, lens_id: lensId, retention,
      });
      router.push(`/processing/${job_id}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Upload failed.");
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-3xl">
      <p className="text-xs font-semibold uppercase tracking-wide text-accent">New session</p>
      <h1 className="mt-1 text-3xl font-semibold text-foreground">Analyse a board pack</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Upload your board documentation to generate a pre-read and challenge sheet,
        shaped by your committee lens.
      </p>

      <h2 className="mt-8 mb-3 text-sm font-semibold text-foreground">1. Upload document</h2>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); pick(e.dataTransfer.files?.[0] ?? null); }}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer rounded-sm border-2 border-dashed p-10 text-center transition-colors ${
          dragging ? "border-accent bg-accent/5" : "border-border bg-card"
        }`}
      >
        <input
          ref={inputRef} type="file" accept="application/pdf" className="hidden"
          onChange={(e) => pick(e.target.files?.[0] ?? null)}
        />
        <Upload className="mx-auto h-8 w-8 text-muted-foreground" />
        {file ? (
          <p className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-foreground">
            <FileText className="h-4 w-4" />{file.name}
          </p>
        ) : (
          <>
            <p className="mt-3 text-sm font-medium text-foreground">Drag and drop your board pack</p>
            <p className="mt-1 text-xs text-muted-foreground">PDF up to 50 pages and 30 MB.</p>
          </>
        )}
      </div>

      <div className="mt-4">
        <label className="text-sm text-muted-foreground">Title</label>
        <input
          value={title} onChange={(e) => setTitle(e.target.value)}
          placeholder="Board pack title"
          className="mt-1 w-full rounded-sm border border-border bg-card px-3 py-2 text-sm text-foreground focus:outline-none"
        />
      </div>

      <h2 className="mt-8 mb-3 text-sm font-semibold text-foreground">2. Governance lens</h2>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {lenses.filter((l) => l.builtin).map((l) => (
          <button
            key={l.id} onClick={() => setLensId(l.id)}
            className={`rounded-sm border px-4 py-3 text-left text-sm transition-colors ${
              lensId === l.id
                ? "border-accent bg-accent/5 font-medium text-accent"
                : "border-border bg-card text-foreground hover:bg-muted"
            }`}
          >
            {l.name}
          </button>
        ))}
      </div>

      <h2 className="mt-8 mb-3 text-sm font-semibold text-foreground">3. Data retention</h2>
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-start gap-3">
            <Shield className="mt-0.5 h-5 w-5 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium text-foreground">
                {retention === "persist" ? "Persisted" : "Ephemeral"}
              </p>
              <p className="text-xs text-muted-foreground">
                {retention === "persist"
                  ? "Pack and analysis are saved to your library."
                  : "Pack and analysis exist only for this session, then are destroyed."}
              </p>
            </div>
          </div>
          <button
            aria-label="Toggle retention"
            onClick={() => setRetention(retention === "persist" ? "ephemeral" : "persist")}
            className={`relative h-6 w-11 rounded-full transition-colors ${
              retention === "persist" ? "bg-accent" : "bg-muted"
            }`}
          >
            <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-card shadow transition-transform ${
              retention === "persist" ? "translate-x-5" : "translate-x-0.5"
            }`} />
          </button>
        </div>
      </Card>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}

      <div className="mt-6">
        <Button onClick={start} disabled={!file || submitting}>
          {submitting ? "Starting…" : "Start analysis"}
        </Button>
      </div>
    </div>
  );
}