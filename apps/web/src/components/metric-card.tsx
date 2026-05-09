"use client";

import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: number | string;
  max?: number;
  unit?: string;
  icon: LucideIcon;
  trend?: {
    value: number;
    label: string;
  };
  grade?: "A" | "B" | "C" | "D" | "F";
  className?: string;
}

const gradeColors: Record<string, { text: string; bg: string }> = {
  A: { text: "text-green-400", bg: "bg-green-500" },
  B: { text: "text-yellow-400", bg: "bg-yellow-500" },
  C: { text: "text-orange-400", bg: "bg-orange-500" },
  D: { text: "text-red-400", bg: "bg-red-500" },
  F: { text: "text-red-600", bg: "bg-red-700" },
};

export function MetricCard({
  label,
  value,
  max = 100,
  unit = "",
  icon: Icon,
  trend,
  grade,
  className,
}: MetricCardProps) {
  const percent = typeof value === "number" ? (value / max) * 100 : 0;
  const color = grade ? gradeColors[grade] : { text: "text-blue-400", bg: "bg-blue-500" };

  return (
    <div className={cn("rounded-xl border border-slate-800 bg-slate-900 p-5", className)}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <Icon className={cn("h-5 w-5", color.text)} />
          <span className="text-sm font-medium text-slate-300">{label}</span>
        </div>
        {trend && (
          <span className="flex items-center gap-0.5 text-xs text-green-400">
            <svg className="h-3 w-3" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
            {trend.label}
          </span>
        )}
      </div>
      <div className="flex items-end gap-3">
        <span className={cn("text-4xl font-bold", color.text)}>
          {value}
          {unit && <span className="text-lg font-semibold text-slate-500 ml-1">{unit}</span>}
        </span>
        {grade && (
          <span className={cn("text-2xl font-bold", color.text)}>{grade}</span>
        )}
      </div>
      {typeof value === "number" && (
        <div className="mt-3 h-1.5 w-full rounded-full bg-slate-800">
          <div
            className={cn("h-1.5 rounded-full transition-all", color.bg)}
            style={{ width: `${percent}%` }}
          />
        </div>
      )}
    </div>
  );
}
