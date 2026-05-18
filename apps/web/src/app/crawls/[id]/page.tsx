"use client";

import { use } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Loader2,
  AlertCircle,
  Calendar,
  ExternalLink,
  Activity,
  Inbox,
  CheckCircle2,
  XCircle,
  Clock,
  Ban,
  ChevronRight,
} from "lucide-react";
import { useCrawl } from "@/lib/queries/useCrawls";
import { useSeoIssues } from "@/lib/queries/useSeoIssues";
import { SEVERITY_LABELS, SEVERITY_VARIANTS } from "@/lib/api/types/seo_issues";
import { CRAWL_STATUS_LABELS, CRAWL_STATUS_VARIANTS } from "@/lib/api/types/crawls";
import { StatusBadge } from "@/components/status-badge";
import { AlertTriangle } from "lucide-react";

function formatDate(isoDate: string): string {
  return new Date(isoDate).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function timeAgo(isoDate: string): string {
  const diff = Date.now() - new Date(isoDate).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function durationSeconds(startedAt: string | null, completedAt: string | null): string {
  if (!startedAt) return "—";
  const start = new Date(startedAt).getTime();
  const end = completedAt ? new Date(completedAt).getTime() : Date.now();
  const secs = Math.floor((end - start) / 1000);
  if (secs < 60) return `${secs}s`;
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins}m ${secs % 60}s`;
  const hrs = Math.floor(mins / 60);
  return `${hrs}h ${mins % 60}m`;
}

const STATUS_ICONS = {
  PENDING: <Clock className="h-4 w-4" />,
  RUNNING: <Activity className="h-4 w-4 animate-pulse" />,
  COMPLETED: <CheckCircle2 className="h-4 w-4" />,
  FAILED: <XCircle className="h-4 w-4" />,
  CANCELLED: <Ban className="h-4 w-4" />,
} as const;

export default function CrawlDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: crawl, isLoading, isError } = useCrawl(id);

  if (isLoading) {
    return (
      <div className="p-6 space-y-6 max-w-4xl mx-auto">
        <div className="flex items-center gap-3">
          <Link
            href="/websites"
            className="flex items-center gap-1 text-sm text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Websites
          </Link>
          <ChevronRight className="h-4 w-4 text-slate-700" />
          <span className="text-sm text-slate-500">Crawl Detail</span>
        </div>
        <div className="flex items-center justify-center py-24">
          <Loader2 className="h-6 w-6 text-slate-500 animate-spin" />
          <span className="ml-3 text-sm text-slate-500">Loading crawl run...</span>
        </div>
      </div>
    );
  }

  if (isError || !crawl) {
    return (
      <div className="p-6 space-y-6 max-w-4xl mx-auto">
        <div className="flex items-center gap-3">
          <Link
            href="/websites"
            className="flex items-center gap-1 text-sm text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Websites
          </Link>
          <ChevronRight className="h-4 w-4 text-slate-700" />
          <span className="text-sm text-slate-500">Crawl Detail</span>
        </div>
        <div className="flex flex-col items-center justify-center py-24 gap-3 rounded-xl border border-red-900/30 bg-red-950/10">
          <AlertCircle className="h-8 w-8 text-red-400" />
          <p className="text-sm text-red-400">Failed to load crawl run.</p>
          <p className="text-xs text-slate-600">Check that the backend is running.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center gap-3">
        <Link
          href="/websites"
          className="flex items-center gap-1 text-sm text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Websites
        </Link>
        <ChevronRight className="h-4 w-4 text-slate-700" />
        <span className="text-sm text-slate-500">Crawl Detail</span>
      </div>

      {/* Page header */}
      <div className="flex items-start gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-slate-800 border border-slate-700">
          {STATUS_ICONS[crawl.status]}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-white">Crawl Run</h1>
            <StatusBadge
              status={CRAWL_STATUS_VARIANTS[crawl.status]}
              label={CRAWL_STATUS_LABELS[crawl.status]}
            />
          </div>
          <p className="text-sm text-slate-500 font-mono mt-1">{crawl.id}</p>
        </div>
      </div>

      {/* Fields */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
        <table className="w-full text-sm">
          <tbody>
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500 w-44">Crawl ID</td>
              <td className="px-4 py-3 text-slate-300 font-mono text-xs break-all">{crawl.id}</td>
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500">Website ID</td>
              <td className="px-4 py-3 text-slate-300 font-mono text-xs break-all">
                <Link
                  href={`/websites/${crawl.website_id}`}
                  className="text-blue-400 hover:text-blue-300"
                >
                  {crawl.website_id}
                </Link>
              </td>
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500">Status</td>
              <td className="px-4 py-3">
                <StatusBadge
                  status={CRAWL_STATUS_VARIANTS[crawl.status]}
                  label={CRAWL_STATUS_LABELS[crawl.status]}
                />
              </td>
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500">Crawl Depth</td>
              <td className="px-4 py-3 text-slate-300">{crawl.crawl_depth ?? "—"}</td>
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500">Max Pages</td>
              <td className="px-4 py-3 text-slate-300">{crawl.max_pages ?? "—"}</td>
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500">Respect Robots</td>
              <td className="px-4 py-3 text-slate-300">
                {crawl.respect_robots ? "Yes" : "No"}
              </td>
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500 flex items-center gap-1">
                <Activity className="h-3 w-3" />
                Started
              </td>
              <td className="px-4 py-3 text-slate-300">
                {crawl.started_at ? formatDate(crawl.started_at) : "—"}
              </td>
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500 flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                Duration
              </td>
              <td className="px-4 py-3 text-slate-300">
                {durationSeconds(crawl.started_at, crawl.completed_at)}
              </td>
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500">Pages Discovered</td>
              <td className="px-4 py-3 text-slate-300">{crawl.pages_discovered}</td>
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500">Pages Crawled</td>
              <td className="px-4 py-3 text-slate-300">{crawl.pages_crawled}</td>
            </tr>
            {crawl.error_message && (
              <tr className="border-b border-slate-800">
                <td className="px-4 py-3 text-slate-500">Error</td>
                <td className="px-4 py-3 text-red-400 text-sm">{crawl.error_message}</td>
              </tr>
            )}
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500 flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                Created
              </td>
              <td className="px-4 py-3 text-slate-300">
                {formatDate(crawl.created_at)} ({timeAgo(crawl.created_at)})
              </td>
            </tr>
            <tr>
              <td className="px-4 py-3 text-slate-500 flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                Updated
              </td>
              <td className="px-4 py-3 text-slate-300">
                {formatDate(crawl.updated_at)} ({timeAgo(crawl.updated_at)})
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Back link */}
      <div className="flex items-center">
        <Link
          href={`/websites/${crawl.website_id}`}
          className="flex items-center gap-1 text-sm text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to website
        </Link>
      </div>

      {/* Related SEO Issues */}
      <SeoIssuesSection crawlId={crawl.id} websiteId={crawl.website_id} />
    </div>
  );
}

function SeoIssuesSection({ crawlId, websiteId }: { crawlId: string; websiteId: string }) {
  const { data, isLoading, isError } = useSeoIssues({ crawlRunId: crawlId, limit: 50 });

  if (isLoading) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="h-4 w-4 text-slate-400" />
          <h2 className="text-base font-semibold text-white">SEO Issues</h2>
        </div>
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-5 w-5 text-slate-500 animate-spin" />
          <span className="ml-2 text-sm text-slate-500">Loading SEO issues...</span>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="h-4 w-4 text-slate-400" />
          <h2 className="text-base font-semibold text-white">SEO Issues</h2>
        </div>
        <div className="flex flex-col items-center justify-center py-8 gap-2 rounded-lg border border-red-900/30 bg-red-950/10">
          <AlertCircle className="h-5 w-5 text-red-400" />
          <p className="text-sm text-red-400">Failed to load SEO issues.</p>
          <p className="text-xs text-slate-600">Check that the backend is running.</p>
        </div>
      </div>
    );
  }

  const issues = data?.items ?? [];

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="h-4 w-4 text-slate-400" />
        <h2 className="text-base font-semibold text-white">SEO Issues</h2>
        {data && (
          <span className="text-xs text-slate-500 ml-auto">{data.total} total</span>
        )}
      </div>

      {issues.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 gap-2 rounded-lg border border-slate-800">
          <Inbox className="h-8 w-8 text-slate-700" />
          <p className="text-sm text-slate-400 font-medium">No SEO issues found for this crawl run.</p>
          <p className="text-xs text-slate-600 text-center max-w-xs">
            No issues were detected in this crawl run.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {issues.map((issue) => (
            <div
              key={issue.id}
              className="flex items-start justify-between rounded-lg border border-slate-800 bg-slate-800/30 px-4 py-3 gap-4"
            >
              <div className="flex flex-col gap-1 min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-slate-200 truncate">
                    {issue.title}
                  </span>
                  <StatusBadge
                    status={SEVERITY_VARIANTS[issue.severity]}
                    label={SEVERITY_LABELS[issue.severity]}
                  />
                </div>
                {issue.description && (
                  <p className="text-xs text-slate-500 line-clamp-2">{issue.description}</p>
                )}
                <div className="flex items-center gap-3 text-xs text-slate-600">
                  <span className="font-mono text-slate-600">{issue.issue_type}</span>
                  <span>{timeAgo(issue.created_at)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}