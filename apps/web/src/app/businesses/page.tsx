"use client";

import { Building2, Globe, Plus, Search, ChevronRight, MoreHorizontal } from "lucide-react";

const businesses = [
  {
    id: "1",
    name: "MTV Tech Solutions",
    domain: "mtvhvac.com",
    industry: "Home Services — HVAC",
    websites: 1,
    lastCrawl: "2h ago",
    seoScore: 72,
  },
  {
    id: "2",
    name: "Green Culture",
    domain: "green-culture.co",
    industry: "Cannabis — Retail",
    websites: 1,
    lastCrawl: "1d ago",
    seoScore: 61,
  },
  {
    id: "3",
    name: "Country Roads Car Services",
    domain: "countryroadsauto.com",
    industry: "Automotive — Car Services",
    websites: 1,
    lastCrawl: "2d ago",
    seoScore: null,
  },
];

export default function BusinessesPage() {
  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Businesses</h1>
          <p className="text-sm text-slate-400 mt-1">Manage your business profiles and websites</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 transition-colors">
          <Plus className="h-4 w-4" />
          Add Business
        </button>
      </div>

      {/* Search */}
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
        {businesses.map((biz) => (
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
                {biz.domain} &middot; {biz.industry}
              </p>
            </div>
            <div className="text-right hidden sm:block">
              <p className="text-xs text-slate-500">SEO Score</p>
              <p className={`text-sm font-semibold ${
                biz.seoScore === null ? "text-slate-600" :
                biz.seoScore >= 80 ? "text-green-400" :
                biz.seoScore >= 60 ? "text-yellow-400" : "text-red-400"
              }`}>
                {biz.seoScore ?? "—"}
              </p>
            </div>
            <div className="text-right hidden sm:block">
              <p className="text-xs text-slate-500">Last Crawl</p>
              <p className="text-sm text-slate-400">{biz.lastCrawl}</p>
            </div>
            <ChevronRight className="h-4 w-4 text-slate-600" />
          </a>
        ))}
      </div>
    </div>
  );
}
