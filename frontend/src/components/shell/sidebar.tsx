"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutGrid, Library, History, Settings } from "lucide-react";
import { cn } from "@/lib/cn";

const MAIN = [
  { href: "/", label: "Dashboard", icon: LayoutGrid },
  { href: "/library", label: "Library", icon: Library },
  { href: "/activity", label: "Activity", icon: History },
];

export function Sidebar({ appName = "Board Preparation Dashboard" }: { appName?: string }) {
  const path = usePathname();
  const isActive = (href: string) =>
    href === "/" ? path === "/" : path.startsWith(href);

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-border bg-background">
      <div className="flex items-center gap-2 px-6 py-5">
        <span className="grid h-8 w-8 place-items-center rounded-sm bg-accent text-accent-foreground">
          <LayoutGrid className="h-4 w-4" />
        </span>
        <span className="text-sm font-semibold text-foreground">{appName}</span>
      </div>

      <nav className="flex-1 px-4 pt-4">
        <p className="px-2 pb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Main menu
        </p>
        <ul className="space-y-1">
          {MAIN.map(({ href, label, icon: Icon }) => (
            <li key={href}>
              <Link
                href={href}
                className={cn(
                  "flex items-center gap-3 rounded-sm px-3 py-2 text-sm transition-colors",
                  isActive(href)
                    ? "bg-accent/10 font-medium text-accent"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div className="border-t border-border px-4 py-4">
        <Link
          href="/settings"
          className={cn(
            "flex items-center gap-3 rounded-sm px-3 py-2 text-sm transition-colors",
            isActive("/settings")
              ? "bg-accent/10 font-medium text-accent"
              : "text-muted-foreground hover:bg-muted hover:text-foreground",
          )}
        >
          <Settings className="h-4 w-4" />
          Account Settings
        </Link>
      </div>
    </aside>
  );
}