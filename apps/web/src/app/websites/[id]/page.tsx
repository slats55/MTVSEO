"use client";

import { use } from "react";
import Link from "next/link";
import { Globe, ArrowLeft, Loader2, AlertCircle, Calendar, ExternalLink } from "lucide-react";
import { useWebsite } from "@/lib/queries/useWebsite";
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

export default function WebsiteDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data, isLoading, isError } = useWebsite(id);

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
  if (!data) {
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

  const website: Website = data;

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

      {/* Related crawls note */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
        <p className="text-sm text-slate-500">
          Related crawl runs are accessible via{" "}
          <code className="text-slate-400 text-xs bg-slate-800 px-1.5 py-0.5 rounded">
            GET /api/v1/crawls/?website_id={id.slice(0, 8)}...
          </code>
          . No crawl history is displayed here as no dedicated endpoint or hook exists for
          website-associated crawls on the detail page.
        </p>
      </div>
    </div>
  );
}