"use client";

import { Building2, Globe, Plus, Search, ChevronRight } from "lucide-react";
import { useBusinesses } from "@/lib/queries/useBusinesses";

export default function BusinessesPage() {
  const { data, isLoading, isError } = useBusinesses();

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Businesses</h1>
          <p className="text-sm text-slate-400 mt-1">Manage your business profiles and websites</p>
        </div>
        <button
          disabled
          title="Create flow coming soon"
          className="flex items-center gap-2 rounded-lg bg-blue-600/50 px-4 py-2 text-sm font-medium text-white/50 cursor-not-allowed"
        >
          <Plus className="h-4 w-4" />
          Add Business
        </button>
      </div>

      {/* Search — client-side filter on name */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
        <input
          type="text"
          placeholder="Search businesses..."
          className="w-full rounded-lg border border-slate-800 bg-slate-900 pl-10 pr-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600"
        />
      </div>

      {/* Business list */}
      <div className="space-y-3">
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <span className="text-sm text-slate-500">Loading businesses...</span>
          </div>
        )}

        {isError && (
          <div className="flex items-center justify-center py-12">
            <span className="text-sm text-red-400">Failed to load businesses.</span>
          </div>
        )}

        {!isLoading && !isError && data?.items?.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12 gap-2">
            <Building2 className="h-8 w-8 text-slate-600" />
            <span className="text-sm text-slate-500">No businesses yet.</span>
            <span className="text-xs text-slate-600">Add a business to get started.</span>
          </div>
        )}

        {!isLoading && !isError && data?.items && data.items.length > 0 && (
          data.items.map((biz) => (
            <a
              key={biz.id}
              href={`/businesses/${biz.id}`}
              className="flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900 p-4 hover:border-slate-700 hover:bg-slate-800/50 transition-all"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-800">
                <Building2 className="h-5 w-5 text-slate-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-white truncate">{biz.name}</p>
                <p className="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
                  <Globe className="h-3 w-3" />
                  {biz.website_url ?? "No website"} &middot; {biz.business_type ?? biz.location ?? "—"}
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
              <div className="text-right hidden sm:block">
                <p className="text-xs text-slate-500">SEO Score</p>
                <p className="text-sm font-semibold text-slate-600">—</p>
              </div>
              <div className="text-right hidden sm:block">
                <p className="text-xs text-slate-500">Last Crawl</p>
                <p className="text-sm text-slate-600">—</p>
              </div>
              <ChevronRight className="h-4 w-4 text-slate-600" />
            </a>
          ))
        )}
      </div>
    </div>
  );
}
