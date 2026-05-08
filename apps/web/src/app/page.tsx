"use client";

import { MetricCard } from "@/components/metric-card";
import { StatusBadge } from "@/components/status-badge";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  ExternalLink,
  FileText,
  Globe,
  RefreshCcw,
  Search,
  TrendingUp,
  ChevronRight,
  BarChart3,
  LineChart,
  Zap,
} from "lucide-react";

// Mock data — replace with API calls via React Query after CRUD stabilizes
const metrics = [
  { label: "Technical SEO", value: 72, max: 100, unit: "", icon: Search, grade: "C" as const, trend: { value: 3, label: "+3" } },
  { label: "GEO / AI Visibility", value: 58, max: 100, unit: "", icon: Activity, grade: "D" as const, trend: { value: 5, label: "+5" } },
  { label: "Content Quality", value: 81, max: 100, unit: "", icon: FileText, grade: "B" as const, trend: { value: 2, label: "+2" } },
  { label: "Crawl Health", value: 94, max: 100, unit: "", icon: Globe, grade: "A" as const },
];

const quickActions = [
  { label: "New Crawl", icon: RefreshCcw, href: "/businesses", description: "Crawl a website" },
  { label: "Run SEO Audit", icon: Search, href: "/audits", description: "Technical analysis" },
  { label: "Run GEO Audit", icon: Activity, href: "/audits", description: "AI visibility check" },
  { label: "Generate Report", icon: FileText, href: "/reports", description: "Export findings" },
];

const recentCrawls = [
  { id: "1", website: "mtvhvac.com", status: "completed", pages: 47, score: 72, date: "2h ago" },
  { id: "2", website: "green-culture.co", status: "completed", pages: 31, score: 61, date: "1d ago" },
  { id: "3", website: "countryroadsauto.com", status: "failed", pages: 12, score: null, date: "2d ago" },
  { id: "4", website: "example.org", status: "completed", pages: 89, score: 85, date: "3d ago" },
];

const topIssues = [
  { severity: "high", count: 3, title: "Missing meta descriptions on 12 pages", category: "On-Page SEO" },
  { severity: "high", count: 2, title: "Duplicate title tags found", category: "On-Page SEO" },
  { severity: "medium", count: 7, title: "Images missing alt text", category: "Images & Media" },
  { severity: "medium", count: 4, title: "Broken internal links (404)", category: "Links" },
  { severity: "low", count: 11, title: "H1 too long (>60 chars)", category: "Headings" },
];

const keywordOpportunities = [
  { keyword: "emergency hvac repair", volume: 2200, difficulty: 45, position: 12, change: "+3" },
  { keyword: "commercial hvac maintenance", volume: 1800, difficulty: 52, position: 24, change: "+1" },
  { keyword: "geothermal heating", volume: 950, difficulty: 38, position: 8, change: "+5" },
];

function getStatusVariant(status: string) {
  switch (status) {
    case "completed":
      return "success" as const;
    case "failed":
      return "error" as const;
    default:
      return "neutral" as const;
  }
}

export default function DashboardPage() {
  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">
            Overview for <span className="text-blue-400 font-medium">MTV Tech Solutions</span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors">
            <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
          <span className="text-xs text-slate-500">Last sync: 5 min ago</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m) => (
          <MetricCard
            key={m.label}
            label={m.label}
            value={m.value}
            max={m.max}
            unit={m.unit}
            icon={m.icon}
            grade={m.grade}
            trend={m.trend}
          />
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {quickActions.map((action) => (
          <a
            key={action.label}
            href={action.href}
            className="group flex flex-col items-start gap-2 rounded-xl border border-slate-800 bg-slate-900 p-4 hover:border-slate-700 hover:bg-slate-800/60 transition-all"
          >
            <div className="flex items-center justify-between w-full">
              <action.icon className="h-5 w-5 text-blue-400 group-hover:text-blue-300" />
              <ChevronRight className="h-4 w-4 text-slate-600 group-hover:text-slate-400" />
            </div>
            <span className="text-sm font-medium text-slate-200">{action.label}</span>
            <span className="text-xs text-slate-500">{action.description}</span>
          </a>
        ))}
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Crawls */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
            <div>
              <h2 className="text-base font-semibold text-white">Recent Crawls</h2>
              <p className="text-xs text-slate-500 mt-0.5">Latest website scans</p>
            </div>
            <a href="/businesses" className="flex items-center gap-1 text-xs text-blue-400 hover:underline">
              View all <ArrowUpRight className="h-3 w-3" />
            </a>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-left text-slate-500">
                  <th className="px-5 py-3 font-medium">Website</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                  <th className="px-5 py-3 font-medium">Pages</th>
                  <th className="px-5 py-3 font-medium">Score</th>
                  <th className="px-5 py-3 font-medium">When</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {recentCrawls.map((crawl) => (
                  <tr key={crawl.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-5 py-3 text-slate-200 font-mono text-xs">{crawl.website}</td>
                    <td className="px-5 py-3">
                      <StatusBadge status={getStatusVariant(crawl.status)} label={crawl.status} />
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
        </div>

        {/* Top Issues */}
        <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
            <div>
              <h2 className="text-base font-semibold text-white">Top Issues</h2>
              <p className="text-xs text-slate-500 mt-0.5">Priority items to fix</p>
            </div>
            <a href="/audits" className="flex items-center gap-1 text-xs text-blue-400 hover:underline">
              View all <ArrowUpRight className="h-3 w-3" />
            </a>
          </div>
          <div className="divide-y divide-slate-800">
            {topIssues.map((issue, i) => (
              <div key={i} className="flex items-start gap-3 px-5 py-3 hover:bg-slate-800/30 transition-colors">
                <div className="mt-0.5">
                  {issue.severity === "high" && <AlertTriangle className="h-4 w-4 text-red-400" />}
                  {issue.severity === "medium" && <AlertTriangle className="h-4 w-4 text-yellow-400" />}
                  {issue.severity === "low" && <BarChart3 className="h-4 w-4 text-blue-400" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-200 leading-relaxed">{issue.title}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-slate-500">{issue.category}</span>
                    <span className="text-xs text-slate-600">•</span>
                    <span className="text-xs text-slate-500">{issue.count} occurrences</span>
                  </div>
                </div>
                <StatusBadge status={issue.severity === "high" ? "error" : issue.severity === "medium" ? "warning" : "info"} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Keyword Opportunities */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
          <div>
            <h2 className="text-base font-semibold text-white">Keyword Opportunities</h2>
            <p className="text-xs text-slate-500 mt-0.5">Quick wins from recent analysis</p>
          </div>
          <a href="/audits" className="flex items-center gap-1 text-xs text-blue-400 hover:underline">
            View keywords <ArrowUpRight className="h-3 w-3" />
          </a>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-left text-slate-500">
                <th className="px-5 py-3 font-medium">Keyword</th>
                <th className="px-5 py-3 font-medium">Vol.</th>
                <th className="px-5 py-3 font-medium">Difficulty</th>
                <th className="px-5 py-3 font-medium">Pos.</th>
                <th className="px-5 py-3 font-medium">Change</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {keywordOpportunities.map((kw, i) => (
                <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-5 py-3 text-slate-200 font-medium">{kw.keyword}</td>
                  <td className="px-5 py-3 text-slate-300">{kw.volume.toLocaleString()}</td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-16 rounded-full bg-slate-800">
                        <div
                          className={`h-1.5 rounded-full ${
                            kw.difficulty < 40 ? "bg-green-500" :
                            kw.difficulty < 60 ? "bg-yellow-500" : "bg-red-500"
                          }`}
                          style={{ width: `${kw.difficulty}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-400">{kw.difficulty}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3 text-slate-300">{kw.position}</td>
                  <td className="px-5 py-3">
                    <span className="text-sm font-semibold text-green-400">{kw.change}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
