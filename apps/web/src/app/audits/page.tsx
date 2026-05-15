"use client";

import { useState } from "react";
import { useSeoIssues } from "@/lib/queries/useSeoIssues";
import { SEVERITY_LABELS, SEVERITY_VARIANTS } from "@/lib/api/types/seo_issues";
import { AlertTriangle, CheckCircle2, FileSearch, Filter, TrendingDown } from "lucide-react";
import { StatusBadge } from "@/components/status-badge";

const severities = ["all", "critical", "high", "medium", "low", "info"] as const;
type SeverityFilter = typeof severities[number];

function timeAgo(isoDate: string): string {
  const diff = Date.now() - new Date(isoDate).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export default function AuditsPage() {
  const [activeSeverity, setActiveSeverity] = useState<SeverityFilter>("all");
  const { data, isLoading, isError } = useSeoIssues();

  const items = data?.items ?? [];
  const total = data?.total ?? 0;

  // Compute severity counts from real data
  const severityCounts = items.reduce<Record<string, number>>((acc, issue) => {
    const key = issue.severity.toLowerCase();
    acc[key] = (acc[key] ?? 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const filtered = activeSeverity === "all"
    ? items
    : items.filter((i) => i.severity.toLowerCase() === activeSeverity);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Technical SEO Audit</h1>
          <p className="text-sm text-slate-400 mt-1">
            {total > 0
              ? `${total} issue${total !== 1 ? "s" : ""} found`
              : "SEO issue overview"}
          </p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors">
            <FileSearch className="h-4 w-4" />
            Run New Audit
          </button>
        </div>
      </div>

      {/* Issue breakdown — computed from real data, no fake scores */}
      {isLoading && (
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-6">
          {severities.slice(1).map((sev) => (
            <div key={sev} className="rounded-lg border border-slate-800 bg-slate-900 p-3 animate-pulse">
              <div className="h-3 bg-slate-800 rounded w-2/3 mb-2" />
              <div className="h-3 bg-slate-800 rounded w-1/3" />
            </div>
          ))}
        </div>
      )}
      {!isLoading && !isError && total === 0 && (
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6 flex flex-col items-center gap-2">
          <CheckCircle2 className="h-8 w-8 text-slate-600" />
          <p className="text-sm text-slate-500">No SEO issues found.</p>
          <p className="text-xs text-slate-600">Run a crawl to start discovering issues.</p>
        </div>
      )}
      {!isLoading && !isError && total > 0 && (
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
          {(["critical", "high", "medium", "low", "info"] as const).map((sev) => {
            const count = Object.entries(severityCounts).find(
              ([k]) => k.toLowerCase() === sev
            )?.[1] ?? 0;
            return (
              <div key={sev} className="rounded-lg border border-slate-800 bg-slate-900 p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-slate-400 capitalize">{SEVERITY_LABELS[sev.toUpperCase() as keyof typeof SEVERITY_LABELS]}</span>
                  <span className={`text-sm font-bold ${
                    sev === "critical" ? "text-red-400" :
                    sev === "high" ? "text-orange-400" :
                    sev === "medium" ? "text-yellow-400" :
                    sev === "low" ? "text-blue-400" :
                    "text-slate-400"
                  }`}>
                    {count}
                  </span>
                </div>
                <div className="h-1 w-full rounded-full bg-slate-800" />
              </div>
            );
          })}
        </div>
      )}

      {/* Severity filter */}
      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="h-4 w-4 text-slate-500" />
        {severities.map((sev) => (
          <button
            key={sev}
            onClick={() => setActiveSeverity(sev)}
            className={`rounded-md px-3 py-1 text-xs font-medium capitalize transition-colors ${
              activeSeverity === sev
                ? sev === "critical" ? "bg-red-900 text-red-400 border border-red-700"
                : sev === "high" ? "bg-orange-900 text-orange-400 border border-orange-700"
                : sev === "medium" ? "bg-yellow-900 text-yellow-400 border border-yellow-700"
                : sev === "low" ? "bg-blue-900 text-blue-400 border border-blue-700"
                : sev === "info" ? "bg-slate-800 text-slate-400 border border-slate-700"
                : "bg-slate-700 text-white border border-slate-600"
                : "bg-slate-900 text-slate-400 border border-slate-800 hover:bg-slate-800"
            }`}
          >
            {sev}
          </button>
        ))}
      </div>

      {/* Issues table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
        <div className="border-b border-slate-800 px-5 py-4">
          <h2 className="text-base font-semibold text-white">
            Issues ({filtered.length})
          </h2>
        </div>
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <span className="text-sm text-slate-500">Loading issues...</span>
          </div>
        )}
        {isError && (
          <div className="flex flex-col items-center justify-center py-12 gap-2">
            <AlertTriangle className="h-8 w-8 text-red-400" />
            <p className="text-sm text-red-400">Failed to load SEO issues.</p>
            <p className="text-xs text-slate-600">Check that the backend is running.</p>
          </div>
        )}
        {!isLoading && !isError && filtered.length === 0 && activeSeverity === "all" && (
          <div className="flex flex-col items-center justify-center py-12 gap-2">
            <CheckCircle2 className="h-8 w-8 text-slate-600" />
            <p className="text-sm text-slate-500">No SEO issues found.</p>
            <p className="text-xs text-slate-600">Run a crawl to start discovering issues.</p>
          </div>
        )}
        {!isLoading && !isError && filtered.length === 0 && activeSeverity !== "all" && (
          <div className="flex flex-col items-center justify-center py-12 gap-2">
            <CheckCircle2 className="h-8 w-8 text-slate-600" />
            <p className="text-sm text-slate-500">No {activeSeverity} severity issues.</p>
          </div>
        )}
        {!isLoading && !isError && filtered.length > 0 && (
          <div className="divide-y divide-slate-800">
            {filtered.map((issue) => (
              <div key={issue.id} className="flex items-start gap-4 px-5 py-4 hover:bg-slate-800/30 transition-colors">
                <span className={`mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                  issue.severity === "CRITICAL" ? "bg-red-900/70 text-red-400" :
                  issue.severity === "HIGH" ? "bg-orange-900/70 text-orange-400" :
                  issue.severity === "MEDIUM" ? "bg-yellow-900/70 text-yellow-400" :
                  issue.severity === "LOW" ? "bg-blue-900/70 text-blue-400" :
                  "bg-slate-800 text-slate-500"
                }`}>
                  {issue.severity === "CRITICAL" ? <AlertTriangle className="h-3 w-3" /> :
                   issue.severity === "HIGH" ? <TrendingDown className="h-3 w-3" /> :
                   issue.severity === "MEDIUM" ? <AlertTriangle className="h-3 w-3" /> :
                   issue.severity === "LOW" ? <CheckCircle2 className="h-3 w-3" /> : "i"}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-200">{issue.title}</p>
                  {issue.affected_element && (
                    <p className="text-xs text-slate-500 mt-0.5 font-mono truncate">{issue.affected_element}</p>
                  )}
                </div>
                <span className="shrink-0 rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-400">
                  {issue.issue_type}
                </span>
                <StatusBadge
                  status={SEVERITY_VARIANTS[issue.severity] ?? "neutral"}
                  label={SEVERITY_LABELS[issue.severity] ?? issue.severity}
                />
                {issue.created_at && (
                  <span className="shrink-0 text-xs text-slate-600">
                    {timeAgo(issue.created_at)}
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}