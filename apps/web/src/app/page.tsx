"use client";

import { StatusBadge } from "@/components/status-badge";
import { useCrawls } from "@/lib/queries/useCrawls";
import { useBusinesses } from "@/lib/queries/useBusinesses";
import { useWebsites } from "@/lib/queries/useWebsites";
import { useSeoIssues } from "@/lib/queries/useSeoIssues";
import { CRAWL_STATUS_LABELS } from "@/lib/api/types/crawls";
import { SEVERITY_LABELS, SEVERITY_VARIANTS } from "@/lib/api/types/seo_issues";
import { Building2 } from "lucide-react";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  FileText,
  Globe,
  RefreshCcw,
  Search,
  ChevronRight,
  BarChart3,
} from "lucide-react";

// Quick actions — static navigation links (no backend dependency)
const quickActions = [
  { label: "New Crawl", icon: RefreshCcw, href: "/websites", description: "Crawl a website" },
  { label: "Run SEO Audit", icon: Search, href: "/audits", description: "Technical analysis" },
  { label: "Run GEO Audit", icon: Activity, href: "/audits", description: "AI visibility check" },
  { label: "Generate Report", icon: FileText, href: "/reports", description: "Export findings" },
];

function getStatusVariant(status: string) {
  switch (status.toLowerCase()) {
    case "completed":
      return "success" as const;
    case "failed":
      return "error" as const;
    case "running":
      return "info" as const;
    default:
      return "neutral" as const;
  }
}

export default function DashboardPage() {
  const { data: crawlData, isLoading: crawlLoading, isError: crawlError } = useCrawls();
  const { data: businessData, isLoading: bizLoading, isError: bizError } = useBusinesses();
  const { data: websiteData, isLoading: siteLoading, isError: siteError } = useWebsites();
  const { data: issueData, isLoading: issueLoading, isError: issueError } = useSeoIssues();

  function timeAgo(isoDate: string): string {
    const diff = Date.now() - new Date(isoDate).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
  }

  const crawlRows = crawlData?.items.slice(0, 4).map((crawl) => ({
    id: crawl.id,
    website_id: crawl.website_id,
    status: crawl.status,
    pages: crawl.pages_crawled,
    date: crawl.started_at ? timeAgo(crawl.started_at) : timeAgo(crawl.created_at),
  })) ?? [];

  const displayCrawls = crawlRows;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">
            {businessData?.items && businessData.items.length > 0
              ? <>Overview for <span className="text-blue-400 font-medium">{businessData.items[0].name}</span></>
              : "SEO Dashboard Overview"}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors">
            <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
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

      {/* Business Projects Overview */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
          <div>
            <h2 className="text-base font-semibold text-white">Business Projects</h2>
            <p className="text-xs text-slate-500 mt-0.5">Active businesses in your account</p>
          </div>
          <a href="/businesses" className="flex items-center gap-1 text-xs text-blue-400 hover:underline">
            Manage <ArrowUpRight className="h-3 w-3" />
          </a>
        </div>
        {bizLoading && (
          <div className="flex items-center justify-center py-8">
            <span className="text-sm text-slate-500">Loading businesses...</span>
          </div>
        )}
        {bizError && (
          <div className="flex items-center justify-center py-8">
            <span className="text-sm text-red-400">Failed to load businesses</span>
          </div>
        )}
        {!bizLoading && !bizError && businessData?.items?.length === 0 && (
          <div className="flex flex-col items-center justify-center py-8 gap-2">
            <Building2 className="h-8 w-8 text-slate-600" />
            <span className="text-sm text-slate-500">No businesses yet.</span>
            <span className="text-xs text-slate-600">Create one from the Businesses page.</span>
          </div>
        )}
        {!bizLoading && !bizError && businessData?.items && businessData.items.length > 0 && (
          <div className="divide-y divide-slate-800">
            {businessData.items.slice(0, 4).map((biz) => (
              <div key={biz.id} className="flex items-center gap-4 px-5 py-3 hover:bg-slate-800/40 transition-colors">
                <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-blue-900/40 text-blue-400">
                  <Building2 className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-200 truncate">{biz.name}</p>
                  <p className="text-xs text-slate-500 truncate">
                    {biz.location ?? biz.business_type ?? "No location"}
                    {biz.website_url && ` — ${biz.website_url}`}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {biz.is_cannabis && (
                    <span className="inline-flex items-center rounded-full bg-green-900/30 px-2 py-0.5 text-xs text-green-400">
                      Cannabis
                    </span>
                  )}
                  {biz.is_ymyl && (
                    <span className="inline-flex items-center rounded-full bg-yellow-900/30 px-2 py-0.5 text-xs text-yellow-400">
                      YMYL
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Websites */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
          <div>
            <h2 className="text-base font-semibold text-white">Websites</h2>
            <p className="text-xs text-slate-500 mt-0.5">Monitored domains</p>
          </div>
          <a href="/websites" className="flex items-center gap-1 text-xs text-blue-400 hover:underline">
            Manage <ArrowUpRight className="h-3 w-3" />
          </a>
        </div>
        {siteLoading && (
          <div className="flex items-center justify-center py-8">
            <span className="text-sm text-slate-500">Loading websites...</span>
          </div>
        )}
        {siteError && (
          <div className="flex items-center justify-center py-8">
            <span className="text-sm text-red-400">Failed to load websites</span>
          </div>
        )}
        {!siteLoading && !siteError && websiteData?.items?.length === 0 && (
          <div className="flex flex-col items-center justify-center py-8 gap-2">
            <Globe className="h-8 w-8 text-slate-600" />
            <span className="text-sm text-slate-500">No websites yet.</span>
            <span className="text-xs text-slate-600">Add a website from the Businesses page.</span>
          </div>
        )}
        {!siteLoading && !siteError && websiteData?.items && websiteData.items.length > 0 && (
          <div className="divide-y divide-slate-800">
            {websiteData.items.slice(0, 4).map((site) => (
              <div key={site.id} className="flex items-center gap-4 px-5 py-3 hover:bg-slate-800/40 transition-colors">
                <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-purple-900/40 text-purple-400">
                  <Globe className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-200 truncate">
                    {site.name ?? site.url}
                  </p>
                  <p className="text-xs text-slate-500 truncate">{site.url}</p>
                </div>
                <span className="text-xs text-slate-600 font-mono truncate max-w-[80px]">{site.business_id.slice(0, 8)}…</span>
              </div>
            ))}
          </div>
        )}
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
            <a href="/audits" className="flex items-center gap-1 text-xs text-blue-400 hover:underline">
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
                  <th className="px-5 py-3 font-medium">When</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {crawlLoading && (
                  <tr>
                    <td colSpan={4} className="px-5 py-8 text-center text-slate-500 text-sm">
                      Loading crawls...
                    </td>
                  </tr>
                )}
                {crawlError && (
                  <tr>
                    <td colSpan={4} className="px-5 py-8 text-center">
                      <span className="text-red-400 text-sm">Failed to load crawls</span>
                    </td>
                  </tr>
                )}
                {!crawlLoading && displayCrawls.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-5 py-8 text-center text-slate-500 text-sm">
                      No crawls yet. Run your first crawl from the Businesses page.
                    </td>
                  </tr>
                )}
                {!crawlLoading && displayCrawls.map((crawl) => (
                  <tr key={crawl.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-5 py-3 text-slate-200 font-mono text-xs">
                      <span title={crawl.website_id}>{crawl.website_id.slice(0, 8)}…</span>
                    </td>
                    <td className="px-5 py-3">
                      <StatusBadge
                        status={getStatusVariant(crawl.status)}
                        label={CRAWL_STATUS_LABELS[crawl.status as keyof typeof CRAWL_STATUS_LABELS] ?? crawl.status}
                      />
                    </td>
                    <td className="px-5 py-3 text-slate-300">{crawl.pages}</td>
                    <td className="px-5 py-3 text-slate-500">{crawl.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* SEO Issues */}
        <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
            <div>
              <h2 className="text-base font-semibold text-white">SEO Issues</h2>
              <p className="text-xs text-slate-500 mt-0.5">Crawl findings</p>
            </div>
            <a href="/audits" className="flex items-center gap-1 text-xs text-blue-400 hover:underline">
              View all <ArrowUpRight className="h-3 w-3" />
            </a>
          </div>
          {issueLoading && (
            <div className="flex items-center justify-center py-8">
              <span className="text-sm text-slate-500">Loading issues...</span>
            </div>
          )}
          {issueError && (
            <div className="flex items-center justify-center py-8">
              <span className="text-sm text-red-400">Failed to load issues</span>
            </div>
          )}
          {!issueLoading && !issueError && issueData?.items?.length === 0 && (
            <div className="flex flex-col items-center justify-center py-8 gap-2">
              <CheckCircle2 className="h-8 w-8 text-slate-600" />
              <span className="text-sm text-slate-500">No SEO issues found.</span>
              <span className="text-xs text-slate-600">Run a crawl to discover issues.</span>
            </div>
          )}
          {!issueLoading && !issueError && issueData?.items && issueData.items.length > 0 && (
            <div className="divide-y divide-slate-800">
              {issueData.items.slice(0, 4).map((issue) => (
                <div key={issue.id} className="flex items-start gap-3 px-5 py-3 hover:bg-slate-800/30 transition-colors">
                  <div className="mt-0.5">
                    {issue.severity === "CRITICAL" || issue.severity === "HIGH" ? (
                      <AlertTriangle className="h-4 w-4 text-red-400" />
                    ) : issue.severity === "MEDIUM" ? (
                      <AlertTriangle className="h-4 w-4 text-yellow-400" />
                    ) : (
                      <BarChart3 className="h-4 w-4 text-blue-400" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-200 leading-relaxed">{issue.title}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-slate-500">{issue.issue_type}</span>
                      {issue.page_id && (
                        <>
                          <span className="text-xs text-slate-600">•</span>
                          <span className="text-xs text-slate-500 font-mono truncate max-w-[60px]">{issue.page_id.slice(0, 8)}…</span>
                        </>
                      )}
                    </div>
                  </div>
                  <StatusBadge
                    status={SEVERITY_VARIANTS[issue.severity] ?? "neutral"}
                    label={SEVERITY_LABELS[issue.severity] ?? issue.severity}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* End of dashboard panels */}
    </div>
  );
}
