"use client";

import { Globe, Plus, Search, ExternalLink, Loader2, AlertCircle, Inbox } from "lucide-react";
import { useWebsites } from "@/lib/queries/useWebsites";

function timeAgo(isoDate: string): string {
  const diff = Date.now() - new Date(isoDate).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export default function WebsitesPage() {
  const { data, isLoading, isError } = useWebsites();

  // Loading state
  if (isLoading) {
    return (
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Websites</h1>
            <p className="text-sm text-slate-400 mt-1">Monitor and manage your tracked websites</p>
          </div>
        </div>
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-6 w-6 text-slate-500 animate-spin" />
          <span className="ml-3 text-sm text-slate-500">Loading websites...</span>
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
            <h1 className="text-2xl font-bold text-white">Websites</h1>
            <p className="text-sm text-slate-400 mt-1">Monitor and manage your tracked websites</p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center py-16 gap-3 rounded-xl border border-red-900/30 bg-red-950/10">
          <AlertCircle className="h-8 w-8 text-red-400" />
          <p className="text-sm text-red-400">Failed to load websites.</p>
          <p className="text-xs text-slate-600">Check that the backend is running.</p>
        </div>
      </div>
    );
  }

  // Empty state — real backend returned no websites
  const websites = data?.items ?? [];
  if (websites.length === 0) {
    return (
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Websites</h1>
            <p className="text-sm text-slate-400 mt-1">Monitor and manage your tracked websites</p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center py-16 gap-3 rounded-xl border border-slate-800 bg-slate-900/50">
          <Inbox className="h-10 w-10 text-slate-700" />
          <p className="text-base font-medium text-slate-400">No websites tracked yet</p>
          <p className="text-sm text-slate-600 text-center max-w-sm">
            Websites are created when businesses are added. Add a business with a website URL to start tracking.
          </p>
        </div>
      </div>
    );
  }

  // Real websites available
  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Websites</h1>
          <p className="text-sm text-slate-400 mt-1">
            {websites.length} website{websites.length !== 1 ? "s" : ""} tracked
          </p>
        </div>
        <button
          disabled
          title="Create website flow coming soon"
          className="flex items-center gap-2 rounded-lg bg-blue-600/50 px-4 py-2 text-sm font-medium text-white/50 cursor-not-allowed"
        >
          <Plus className="h-4 w-4" />
          Add Website
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
        <input
          type="text"
          placeholder="Search websites..."
          className="w-full rounded-lg border border-slate-800 bg-slate-900 pl-10 pr-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600"
        />
      </div>

      {/* Website list */}
      <div className="space-y-3">
        {websites.map((site) => (
          <div
            key={site.id}
            className="flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900 p-4 hover:border-slate-700 hover:bg-slate-800/50 transition-all"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-800">
              <Globe className="h-5 w-5 text-slate-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-white truncate">{site.name ?? site.url}</p>
              <a
                href={site.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-slate-500 flex items-center gap-1 hover:text-blue-400 transition-colors truncate"
              >
                {site.url}
                <ExternalLink className="h-3 w-3 flex-shrink-0" />
              </a>
            </div>
            <div className="text-right hidden sm:block">
              <p className="text-xs text-slate-500">Added</p>
              <p className="text-sm text-slate-400">{timeAgo(site.created_at)}</p>
            </div>
            <div className="text-right hidden sm:block">
              <p className="text-xs text-slate-500">Updated</p>
              <p className="text-sm text-slate-600">{timeAgo(site.updated_at)}</p>
            </div>
            <div className="text-right hidden md:block">
              <p className="text-xs text-slate-500">Business ID</p>
              <p className="text-xs text-slate-600 font-mono">{site.business_id.slice(0, 8)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}