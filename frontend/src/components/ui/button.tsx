import { cn } from "@/lib/cn";
import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md";

const variants: Record<Variant, string> = {
  primary: "bg-accent text-accent-foreground hover:opacity-90",
  secondary: "bg-card text-foreground border border-border hover:bg-muted",
  ghost: "bg-transparent text-muted-foreground hover:text-foreground hover:bg-muted",
  danger: "bg-transparent text-danger border border-border hover:bg-danger/5",
};
const sizes: Record<Size, string> = {
  sm: "h-9 px-3 text-sm",
  md: "h-11 px-4 text-sm",
};

export function Button({
  variant = "primary", size = "md", className, ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: Size }) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-sm font-medium",
        "transition-colors disabled:opacity-40 disabled:pointer-events-none",
        variants[variant], sizes[size], className,
      )}
      {...props}
    />
  );
}
