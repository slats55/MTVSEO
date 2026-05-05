"use client";

import { FileText, Download, Eye, Calendar, TrendingUp } from "lucide-react";

const reports = [
  {
    id: "1",
    title: "Technical SEO Audit — mtvhvac.com",
    type: "technical_seo",
    website: "mtvhvac.com",
    generatedAt: "2026-05-05 10:30 AM",
    seoScore: 72,
    geoScore: 58,
    pages: 47,
  },
  {
    id: "2",
    title: "GEO Audit — mtvhvac.com",
    type: "geo_audit",
    website: "mtvhvac.com",
    generatedAt: "2026-05-05 10:45 AM",
    seoScore: null,
    geoScore: 58,
    pages: 47,
  },
  {
    id: "3",
    title: "Crawl Summary — green-culture.co",
    type: "crawl_summary",
    website: "green-culture.co",
    generatedAt: "2026-05-04 3:15 PM",
    seoScore: 61,
    geoScore: null,
    pages: 31,
  },
  {
    id: "4",
    title: "Content Analysis — countryroadsauto.com",
    type: "content_analysis",
    website: "countryroadsauto.com",
    generatedAt: "2026-05-03 9:00 AM",
    seoScore: null,
    geoScore: null,
    pages: 12,
  },
];

const typeLabels: Record<string, string> = {
  technical_seo: "SEO Audit",
  geo_audit: "GEO Audit",
  crawl_summary: "Crawl Summary",
  content_analysis: "Content Analysis",
};

export default function ReportsPage() {
  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Reports</h1>
          <p className="text-sm text-slate-400 mt-1">View and download generated audit reports</p>
        </div>
      </div>

      {/* Reports grid */}
      <div className="grid gap-4 lg:grid-cols-2">
        {reports.map((report) => (
          <div
            key={report.id}
            className="rounded-xl border border-slate-800 bg-slate-900 p-5 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-slate-500" />
                <span className="rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-400">
                  {typeLabels[report.type]}
                </span>
              </div>
              <div className="flex gap-1">
                <button className="rounded p-1.5 text-slate-500 hover:bg-slate-800 hover:text-slate-300 transition-colors">
                  <Eye className="h-4 w-4" />
                </button>
                <button className="rounded p-1.5 text-slate-500 hover:bg-slate-800 hover:text-slate-300 transition-colors">
                  <Download className="h-4 w-4" />
                </button>
              </div>
            </div>
            <h3 className="font-semibold text-white mb-1">{report.title}</h3>
            <p className="text-xs text-slate-500 font-mono mb-3">{report.website}</p>
            <div className="flex items-center gap-4 text-xs text-slate-500 mb-3">
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {report.generatedAt}
              </span>
              <span>{report.pages} pages</span>
            </div>
            <div className="flex gap-3">
              {report.seoScore !== null && (
                <div className="flex items-center gap-1.5">
                  <TrendingUp className={`h-3.5 w-3.5 ${report.seoScore >= 80 ? "text-green-400" : report.seoScore >= 60 ? "text-yellow-400" : "text-red-400"}`} />
                  <span className="text-xs text-slate-400">SEO: <strong className={report.seoScore >= 80 ? "text-green-400" : report.seoScore >= 60 ? "text-yellow-400" : "text-red-400"}>{report.seoScore}</strong></span>
                </div>
              )}
              {report.geoScore !== null && (
                <div className="flex items-center gap-1.5">
                  <TrendingUp className={`h-3.5 w-3.5 ${report.geoScore >= 80 ? "text-green-400" : report.geoScore >= 60 ? "text-yellow-400" : "text-red-400"}`} />
                  <span className="text-xs text-slate-400">GEO: <strong className={report.geoScore >= 80 ? "text-green-400" : report.geoScore >= 60 ? "text-yellow-400" : "text-red-400"}>{report.geoScore}</strong></span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
