import { ExternalLink } from "lucide-react";
import type { Source } from "@/types/api";

function domain(url: string): string {
  try { return new URL(url).hostname.replace(/^www\./, ""); }
  catch { return url; }
}

export function SourceChip({ source }: { source: Source }) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      title={source.snippet}
      className="inline-flex items-center gap-1.5 rounded-sm border border-border bg-card px-2.5 py-1.5 text-xs text-foreground hover:bg-muted transition-colors"
    >
      <span className="grid h-4 w-4 place-items-center rounded-[3px] bg-muted text-[9px] font-semibold text-muted-foreground">
        {domain(source.url)[0]?.toUpperCase() ?? "?"}
      </span>
      <span className="max-w-[180px] truncate text-muted-foreground">{domain(source.url)}</span>
      <ExternalLink className="h-3 w-3 text-muted-foreground" />
    </a>
  );
}
