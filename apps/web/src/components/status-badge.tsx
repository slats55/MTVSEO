"use client";

import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: "success" | "warning" | "error" | "info" | "neutral";
  label?: string;
  className?: string;
}

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const styles = {
    success: "bg-green-900/50 text-green-400 border-green-700",
    warning: "bg-yellow-900/50 text-yellow-400 border-yellow-700",
    error: "bg-red-900/50 text-red-400 border-red-700",
    info: "bg-blue-900/50 text-blue-400 border-blue-700",
    neutral: "bg-slate-800 text-slate-400 border-slate-700",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2.5 py-1 text-xs font-semibold uppercase tracking-wide",
        styles[status],
        className
      )}
    >
      {label || status}
    </span>
  );
}
