"use client";

import { useCrawls } from "@/lib/queries/useCrawls";
import { CRAWL_STATUS_LABELS, CRAWL_STATUS_VARIANTS } from "@/lib/api/types/crawls";
import { FileText, Download, Eye, Calendar, TrendingUp, Loader2, AlertCircle, Inbox } from "lucide-react";
import { StatusBadge } from "@/components/status-badge";

function timeAgo(isoDate: string): string {
  const diff = Date.now() - new Date(isoDate).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export default function ReportsPage() {
  const { data, isLoading, isError } = useCrawls();

  const completedCrawls = data?.items.filter(
    (c) => c.status === "COMPLETED"
  ) ?? [];
  const total = data?.total ?? 0;

  // Loading state
  if (isLoading) {
    return (
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Reports</h1>
            <p className="text-sm text-slate-400 mt-1">View and download generated audit reports</p>
          </div>
        </div>
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-6 w-6 text-slate-500 animate-spin" />
          <span className="ml-3 text-sm text-slate-500">Loading reports...</span>
        </div>
      </div>
    );
  }

  // Error state
  if (isError) {
    return (
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Reports</h1>
            <p className="text-sm text-slate-400 mt-1">View and download generated audit reports</p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center py-16 gap-3 rounded-xl border border-red-900/30 bg-red-950/10">
          <AlertCircle className="h-8 w-8 text-red-400" />
          <p className="text-sm text-red-400">Failed to load reports.</p>
          <p className="text-xs text-slate-600">Check that the backend is running.</p>
        </div>
      </div>
    );
  }

  // No completed crawls — honest empty state
  if (completedCrawls.length === 0) {
    return (
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Reports</h1>
            <p className="text-sm text-slate-400 mt-1">View and download generated audit reports</p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center py-16 gap-3 rounded-xl border border-slate-800 bg-slate-900/50">
          <Inbox className="h-10 w-10 text-slate-700" />
          <p className="text-base font-medium text-slate-400">No reports available yet</p>
          <p className="text-sm text-slate-600 text-center max-w-sm">
            Reports are generated from completed crawl runs. Run and complete a crawl first,
            then generated reports will appear here.
          </p>
          {total > 0 && (
            <div className="mt-2 rounded-lg bg-slate-800/50 border border-slate-800 px-4 py-2">
              <p className="text-xs text-slate-500">
                {total} crawl{total !== 1 ? "s" : ""} in progress or pending
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Real completed crawls available — show as report rows
  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Reports</h1>
          <p className="text-sm text-slate-400 mt-1">
            {completedCrawls.length} report{completedCrawls.length !== 1 ? "s" : ""} from completed crawls
          </p>
        </div>
      </div>

      {/* Reports grid */}
      <div className="grid gap-4 lg:grid-cols-2">
        {completedCrawls.map((crawl) => {
          const label = `Crawl Report`;
          return (
            <div
              key={crawl.id}
              className="rounded-xl border border-slate-800 bg-slate-900 p-5 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-slate-500" />
                  <span className="rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-400">
                    {label}
                  </span>
                </div>
                <div className="flex gap-1">
                  <button
                    className="rounded p-1.5 text-slate-500 hover:bg-slate-800 hover:text-slate-300 transition-colors"
                    title="View details (not implemented)"
                    disabled
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  <button
                    className="rounded p-1.5 text-slate-500 hover:bg-slate-800 hover:text-slate-300 transition-colors"
                    title="Download report (not implemented)"
                    disabled
                  >
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <h3 className="font-semibold text-white mb-1">Crawl Report — {crawl.website_id.slice(0, 8)}</h3>
              <p className="text-xs text-slate-500 font-mono mb-3">{crawl.website_id}</p>
              <div className="flex items-center gap-4 text-xs text-slate-500 mb-3">
                {crawl.completed_at && (
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {timeAgo(crawl.completed_at)}
                  </span>
                )}
                {crawl.pages_crawled > 0 && (
                  <span>{crawl.pages_crawled} pages crawled</span>
                )}
              </div>
              <div className="flex gap-3">
                <StatusBadge
                  status={CRAWL_STATUS_VARIANTS[crawl.status]}
                  label={CRAWL_STATUS_LABELS[crawl.status]}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}