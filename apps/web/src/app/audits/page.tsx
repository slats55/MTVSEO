"use client";

import { useState } from "react";
import { AlertTriangle, CheckCircle2, FileSearch, Filter, TrendingDown } from "lucide-react";

const severities = ["all", "critical", "high", "medium", "low", "info"];

const issues = [
  { severity: "critical", category: "Crawlability", title: "Crawl blocked by robots.txt on /admin/", url: "mtvhvac.com/admin/", count: 1 },
  { severity: "high", category: "On-Page SEO", title: "Missing meta description", url: "mtvhvac.com/services/", count: 4 },
  { severity: "high", category: "On-Page SEO", title: "Duplicate title tags", url: "mtvhvac.com/blog/", count: 2 },
  { severity: "high", category: "Structured Data", title: "Missing Organization schema on homepage", url: "mtvhvac.com/", count: 1 },
  { severity: "medium", category: "Images & Media", title: "Images missing alt text", url: "mtvhvac.com/portfolio/", count: 7 },
  { severity: "medium", category: "Links & Navigation", title: "Broken internal links (404)", url: "mtvhvac.com/about/", count: 4 },
  { severity: "medium", category: "Headings", title: "H1 too long (>60 characters)", url: "mtvhvac.com/blog/seo-tips/", count: 3 },
  { severity: "low", category: "Content Quality", title: "Thin content (<300 words)", url: "mtvhvac.com/privacy/", count: 2 },
  { severity: "info", category: "Performance", title: "No browser caching headers", url: "mtvhvac.com/static/", count: 5 },
];

const scoreBreakdown = [
  { label: "Crawlability", score: 82, weight: 20 },
  { label: "Indexability", score: 90, weight: 20 },
  { label: "On-Page SEO", score: 61, weight: 30 },
  { label: "Performance", score: 75, weight: 10 },
  { label: "Structured Data", score: 55, weight: 10 },
  { label: "Security", score: 100, weight: 10 },
];

export default function AuditsPage() {
  const [activeSeverity, setActiveSeverity] = useState("all");

  const filtered = activeSeverity === "all"
    ? issues
    : issues.filter((i) => i.severity === activeSeverity);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Technical SEO Audit</h1>
          <p className="text-sm text-slate-400 mt-1">mtvhvac.com &mdash; Last run: 2 hours ago</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors">
            <FileSearch className="h-4 w-4" />
            Run New Audit
          </button>
        </div>
      </div>

      {/* Score breakdown */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-6">
        {scoreBreakdown.map((cat) => (
          <div key={cat.label} className="rounded-lg border border-slate-800 bg-slate-900 p-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-400">{cat.label}</span>
              <span className={`text-sm font-bold ${cat.score >= 80 ? "text-green-400" : cat.score >= 60 ? "text-yellow-400" : "text-red-400"}`}>
                {cat.score}
              </span>
            </div>
            <div className="h-1 w-full rounded-full bg-slate-800">
              <div
                className={`h-1 rounded-full ${cat.score >= 80 ? "bg-green-500" : cat.score >= 60 ? "bg-yellow-500" : "bg-red-500"}`}
                style={{ width: `${cat.score}%` }}
              />
            </div>
          </div>
        ))}
      </div>

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
        <div className="divide-y divide-slate-800">
          {filtered.map((issue, i) => (
            <div key={i} className="flex items-start gap-4 px-5 py-4 hover:bg-slate-800/30 transition-colors">
              <span className={`mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                issue.severity === "critical" ? "bg-red-900/70 text-red-400" :
                issue.severity === "high" ? "bg-orange-900/70 text-orange-400" :
                issue.severity === "medium" ? "bg-yellow-900/70 text-yellow-400" :
                issue.severity === "low" ? "bg-blue-900/70 text-blue-400" :
                "bg-slate-800 text-slate-500"
              }`}>
                {issue.severity === "critical" ? <AlertTriangle className="h-3 w-3" /> :
                 issue.severity === "high" ? <TrendingDown className="h-3 w-3" /> :
                 issue.severity === "medium" ? <AlertTriangle className="h-3 w-3" /> :
                 issue.severity === "low" ? <CheckCircle2 className="h-3 w-3" /> : "i"}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-200">{issue.title}</p>
                <p className="text-xs text-slate-500 mt-0.5 font-mono">{issue.url}</p>
              </div>
              <span className="shrink-0 rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-400">
                {issue.category}
              </span>
              {issue.count > 1 && (
                <span className="shrink-0 rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-500">
                  ×{issue.count}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
