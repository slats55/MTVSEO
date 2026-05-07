"use client";

import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  FileText,
  Globe,
  RefreshCcw,
  Search,
  TrendingUp,
} from "lucide-react";

// Mock data — replace with API calls via React Query
const mockSeoScore = 72;
const mockGeoScore = 58;
const recentCrawls = [
  { id: "1", website: "mtvhvac.com", status: "completed", pages: 47, score: 72, date: "2h ago" },
  { id: "2", website: "green-culture.co", status: "completed", pages: 31, score: 61, date: "1d ago" },
  { id: "3", website: "countryroadsauto.com", status: "failed", pages: 12, score: null, date: "2d ago" },
];

const quickActions = [
  { label: "New Crawl", icon: RefreshCcw, href: "/businesses", color: "text-blue-400" },
  { label: "Run SEO Audit", icon: Search, href: "/audits", color: "text-orange-400" },
  { label: "Run GEO Audit", icon: Activity, href: "/audits", color: "text-purple-400" },
  { label: "Generate Report", icon: ExternalLink, href: "/reports", color: "text-green-400" },
];

function ScoreCard({
  label,
  score,
  grade,
  icon: Icon,
  trend,
}: {
  label: string;
  score: number;
  grade: string;
  icon: React.ElementType;
  trend?: string;
}) {
  const colorMap: Record<string, string> = {
    A: "text-green-400",
    B: "text-yellow-400",
    C: "text-orange-400",
    D: "text-red-400",
    F: "text-red-600",
  };
  const barColor: Record<string, string> = {
    A: "bg-green-500",
    B: "bg-yellow-500",
    C: "bg-orange-500",
    D: "bg-red-500",
    F: "bg-red-700",
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <Icon className={`h-5 w-5 ${colorMap[grade]}`} />
          <span className="text-sm font-medium text-slate-300">{label}</span>
        </div>
        {trend && (
          <span className="flex items-center gap-0.5 text-xs text-green-400">
            <TrendingUp className="h-3 w-3" /> {trend}
          </span>
        )}
      </div>
      <div className="flex items-end gap-3">
        <span className={`text-4xl font-bold ${colorMap[grade]}`}>{score}</span>
        <span className="text-lg font-semibold text-slate-500">/100</span>
        <span className={`ml-1 text-2xl font-bold ${colorMap[grade]}`}>{grade}</span>
      </div>
      <div className="mt-3 h-1.5 w-full rounded-full bg-slate-800">
        <div
          className={`h-1.5 rounded-full transition-all ${barColor[grade]}`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-sm text-slate-400 mt-1">
          Overview for <span className="text-blue-400">MTV Tech Solutions</span>
        </p>
      </div>

      {/* Score cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <ScoreCard label="Technical SEO" score={mockSeoScore} grade="C" icon={Search} trend="+3" />
        <ScoreCard label="GEO / AI Visibility" score={mockGeoScore} grade="D" icon={Activity} trend="+5" />
        <ScoreCard label="Content Quality" score={81} grade="B" icon={FileText} trend="+2" />
        <ScoreCard label="Crawl Health" score={94} grade="A" icon={Globe} />
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {quickActions.map((action) => (
          <a
            key={action.label}
            href={action.href}
            className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 hover:border-slate-700 hover:bg-slate-800/50 transition-all"
          >
            <action.icon className={`h-5 w-5 ${action.color}`} />
            <span className="text-sm font-medium text-slate-200">{action.label}</span>
          </a>
        ))}
      </div>

      {/* Recent crawls */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
          <h2 className="text-base font-semibold text-white">Recent Crawls</h2>
          <a href="/businesses" className="text-xs text-blue-400 hover:underline">
            View all
          </a>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-800 text-left text-slate-500">
              <th className="px-5 py-3 font-medium">Website</th>
              <th className="px-5 py-3 font-medium">Status</th>
              <th className="px-5 py-3 font-medium">Pages</th>
              <th className="px-5 py-3 font-medium">SEO Score</th>
              <th className="px-5 py-3 font-medium">When</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {recentCrawls.map((crawl) => (
              <tr key={crawl.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="px-5 py-3 text-slate-200 font-mono text-xs">{crawl.website}</td>
                <td className="px-5 py-3">
                  {crawl.status === "completed" ? (
                    <span className="inline-flex items-center gap-1 text-green-400">
                      <CheckCircle2 className="h-3.5 w-3.5" /> Completed
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-red-400">
                      <AlertTriangle className="h-3.5 w-3.5" /> Failed
                    </span>
                  )}
                </td>
                <td className="px-5 py-3 text-slate-300">{crawl.pages}</td>
                <td className="px-5 py-3">
                  {crawl.score ? (
                    <span className={`font-semibold ${
                      crawl.score >= 80 ? "text-green-400" :
                      crawl.score >= 60 ? "text-yellow-400" : "text-red-400"
                    }`}>
                      {crawl.score}
                    </span>
                  ) : (
                    <span className="text-slate-600">—</span>
                  )}
                </td>
                <td className="px-5 py-3 text-slate-500">{crawl.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Top issues summary */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
          <h2 className="text-base font-semibold text-white">Top Issues</h2>
          <a href="/audits" className="text-xs text-blue-400 hover:underline">
            View all issues
          </a>
        </div>
        <div className="divide-y divide-slate-800">
          {[
            { severity: "high", count: 3, title: "Missing meta descriptions on 12 pages", cat: "On-Page SEO" },
            { severity: "high", count: 2, title: "Duplicate title tags found", cat: "On-Page SEO" },
            { severity: "medium", count: 7, title: "Images missing alt text", cat: "Images & Media" },
            { severity: "medium", count: 4, title: "Broken internal links (404)", cat: "Links & Navigation" },
            { severity: "low", count: 11, title: "H1 too long (>60 chars)", cat: "Headings" },
          ].map((issue, i) => (
            <div key={i} className="flex items-center gap-4 px-5 py-3">
              <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold uppercase tracking-wide ${
                issue.severity === "high" ? "bg-red-900/50 text-red-400" :
                issue.severity === "medium" ? "bg-yellow-900/50 text-yellow-400" :
                "bg-blue-900/50 text-blue-400"
              }`}>
                {issue.severity}
              </span>
              <span className="flex-1 text-sm text-slate-300">{issue.title}</span>
              <span className="text-xs text-slate-600 bg-slate-800 px-2 py-0.5 rounded">
                {issue.count}×{issue.cat}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
