"use client";

import { use } from "react";
import Link from "next/link";
import {
  Globe,
  ArrowLeft,
  Loader2,
  AlertCircle,
  Calendar,
  ExternalLink,
  Inbox,
  Activity,
  AlertTriangle,
} from "lucide-react";
import { useWebsite } from "@/lib/queries/useWebsite";
import { useWebsiteCrawls } from "@/lib/queries/useWebsiteCrawls";
import { useSeoIssues } from "@/lib/queries/useSeoIssues";
import { SEVERITY_LABELS, SEVERITY_VARIANTS } from "@/lib/api/types/seo_issues";
import { CRAWL_STATUS_LABELS, CRAWL_STATUS_VARIANTS } from "@/lib/api/types/crawls";
import { StatusBadge } from "@/components/status-badge";
import type { Website } from "@/lib/api/types/websites";

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

export default function WebsiteDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: website, isLoading, isError } = useWebsite(id);

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
        </div>
        <div className="flex items-center justify-center py-24">
          <Loader2 className="h-6 w-6 text-slate-500 animate-spin" />
          <span className="ml-3 text-sm text-slate-500">Loading website...</span>
        </div>
      </div>
    );
  }

  if (isError) {
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
        </div>
        <div className="flex flex-col items-center justify-center py-24 gap-3 rounded-xl border border-red-900/30 bg-red-950/10">
          <AlertCircle className="h-8 w-8 text-red-400" />
          <p className="text-sm text-red-400">Failed to load website.</p>
          <p className="text-xs text-slate-600">Check that the backend is running.</p>
        </div>
      </div>
    );
  }

  // This should never happen: loading and error are handled above
  if (!website) {
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
        </div>
        <div className="flex flex-col items-center justify-center py-24 gap-3 rounded-xl border border-red-900/30 bg-red-950/10">
          <AlertCircle className="h-8 w-8 text-red-400" />
          <p className="text-sm text-red-400">Website data unavailable.</p>
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
        <span className="text-slate-700">/</span>
        <span className="text-sm text-slate-500 truncate">{website.name ?? website.url}</span>
      </div>

      {/* Page header */}
      <div className="flex items-start gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-slate-800 border border-slate-700">
          <Globe className="h-7 w-7 text-slate-400" />
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl font-bold text-white">{website.name ?? website.url}</h1>
          <a
            href={website.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-sm text-slate-400 hover:text-blue-400 transition-colors mt-1"
          >
            {website.url}
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>
      </div>

      {/* Fields */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
        <table className="w-full text-sm">
          <tbody>
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500 w-40">Website ID</td>
              <td className="px-4 py-3 text-slate-300 font-mono text-xs break-all">{website.id}</td>
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500">Business ID</td>
              <td className="px-4 py-3 text-slate-300 font-mono text-xs break-all">{website.business_id}</td>
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500">URL</td>
              <td className="px-4 py-3 text-slate-300">
                <a
                  href={website.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 flex items-center gap-1"
                >
                  {website.url}
                  <ExternalLink className="h-3 w-3" />
                </a>
              </td>
            </tr>
            {website.name && (
              <tr className="border-b border-slate-800">
                <td className="px-4 py-3 text-slate-500">Name</td>
                <td className="px-4 py-3 text-slate-300">{website.name}</td>
              </tr>
            )}
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-slate-500 flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                Created
              </td>
              <td className="px-4 py-3 text-slate-300">{formatDate(website.created_at)}</td>
            </tr>
            <tr>
              <td className="px-4 py-3 text-slate-500 flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                Updated
              </td>
              <td className="px-4 py-3 text-slate-300">{formatDate(website.updated_at)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Crawl History Section */}
      <CrawlHistorySection websiteId={id} />

      {/* SEO Issues Section */}
      <SeoIssuesSection websiteId={id} />
    </div>
  );
}

function CrawlHistorySection({ websiteId }: { websiteId: string }) {
  const { data, isLoading, isError } = useWebsiteCrawls(websiteId);

  if (isLoading) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="h-4 w-4 text-slate-400" />
          <h2 className="text-base font-semibold text-white">Crawl History</h2>
        </div>
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-5 w-5 text-slate-500 animate-spin" />
          <span className="ml-2 text-sm text-slate-500">Loading crawl history...</span>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="h-4 w-4 text-slate-400" />
          <h2 className="text-base font-semibold text-white">Crawl History</h2>
        </div>
        <div className="flex flex-col items-center justify-center py-8 gap-2 rounded-lg border border-red-900/30 bg-red-950/10">
          <AlertCircle className="h-5 w-5 text-red-400" />
          <p className="text-sm text-red-400">Failed to load crawl history.</p>
          <p className="text-xs text-slate-600">Check that the backend is running.</p>
        </div>
      </div>
    );
  }

  const crawls = data?.items ?? [];

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="h-4 w-4 text-slate-400" />
        <h2 className="text-base font-semibold text-white">Crawl History</h2>
        {data && (
          <span className="text-xs text-slate-500 ml-auto">{data.total} total</span>
        )}
      </div>

      {crawls.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 gap-2 rounded-lg border border-slate-800">
          <Inbox className="h-8 w-8 text-slate-700" />
          <p className="text-sm text-slate-400 font-medium">No crawl runs found for this website yet.</p>
          <p className="text-xs text-slate-600 text-center max-w-xs">
            Trigger a crawl from the Audits page to see history here.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {crawls.map((crawl) => (
            <Link
              key={crawl.id}
              href={`/crawls/${crawl.id}`}
              className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-800/30 px-4 py-3 hover:border-slate-600 transition-colors"
            >
              <div className="flex flex-col gap-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-mono text-slate-400 text-xs truncate">
                    {crawl.id.slice(0, 8)}...
                  </span>
                  <StatusBadge
                    status={CRAWL_STATUS_VARIANTS[crawl.status]}
                    label={CRAWL_STATUS_LABELS[crawl.status]}
                  />
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-500">
                  <span title={formatDate(crawl.created_at)}>
                    {timeAgo(crawl.created_at)}
                  </span>
                  {crawl.started_at && (
                    <span>
                      Started {timeAgo(crawl.started_at)}
                    </span>
                  )}
                  {crawl.pages_crawled > 0 && (
                    <span>{crawl.pages_crawled} pages crawled</span>
                  )}
                  {crawl.pages_discovered > 0 && (
                    <span>{crawl.pages_discovered} discovered</span>
                  )}
                </div>
              </div>
              <div className="flex flex-col items-end gap-1">
                {crawl.error_message && (
                  <span className="text-xs text-red-400 max-w-[200px] truncate" title={crawl.error_message}>
                    {crawl.error_message}
                  </span>
                )}
                {crawl.completed_at && (
                  <span className="text-xs text-slate-600">
                    Done {timeAgo(crawl.completed_at)}
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function SeoIssuesSection({ websiteId }: { websiteId: string }) {
  const { data: crawlsData, isLoading: crawlsLoading } = useWebsiteCrawls(websiteId);

  // Get real crawl run IDs for this website
  const crawlRunIds = crawlsData?.items?.map((c) => c.id) ?? [];

  // Fetch SEO issues for all crawl runs of this website
  // We query once per crawl run and filter client-side
  // (API does not support website_id filter, only crawl_run_id)
  const { data, isLoading, isError } = useSeoIssues({
    // Fetch issues for all crawl runs; UI filters by crawlRunId
    limit: 50,
  });

  if (crawlsLoading) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="h-4 w-4 text-slate-400" />
          <h2 className="text-base font-semibold text-white">SEO Issues</h2>
        </div>
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-5 w-5 text-slate-500 animate-spin" />
          <span className="ml-2 text-sm text-slate-500">Loading crawl history first...</span>
        </div>
      </div>
    );
  }

  if (crawlRunIds.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="h-4 w-4 text-slate-400" />
          <h2 className="text-base font-semibold text-white">SEO Issues</h2>
        </div>
        <div className="flex flex-col items-center justify-center py-8 gap-2 rounded-lg border border-slate-800">
          <Inbox className="h-8 w-8 text-slate-700" />
          <p className="text-sm text-slate-400 font-medium">No crawl runs yet.</p>
          <p className="text-xs text-slate-600 text-center max-w-xs">
            Run a crawl from the Audits page to generate SEO issues for this website.
          </p>
        </div>
      </div>
    );
  }

  // Filter issues client-side to only those belonging to this website's crawl runs
  const websiteIssues = data?.items?.filter((issue) =>
    crawlRunIds.includes(issue.crawl_run_id)
  ) ?? [];

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

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="h-4 w-4 text-slate-400" />
        <h2 className="text-base font-semibold text-white">SEO Issues</h2>
        {data && (
          <span className="text-xs text-slate-500 ml-auto">{data.total} total</span>
        )}
      </div>

      {websiteIssues.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 gap-2 rounded-lg border border-slate-800">
          <Inbox className="h-8 w-8 text-slate-700" />
          <p className="text-sm text-slate-400 font-medium">No SEO issues found for this website.</p>
          <p className="text-xs text-slate-600 text-center max-w-xs">
            No issues were detected in the completed crawl runs for this website.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {websiteIssues.map((issue) => (
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