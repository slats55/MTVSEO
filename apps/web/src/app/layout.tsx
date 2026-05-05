"use client";

import "./globals.css";
import Link from "next/link";
import {
  LayoutDashboard,
  Building2,
  FileSearch,
  FileText,
  Settings,
  ChevronDown,
} from "lucide-react";
import { useState } from "react";

const navItems = [
  { href: "/", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/businesses", icon: Building2, label: "Businesses" },
  { href: "/audits", icon: FileSearch, label: "Audits" },
  { href: "/reports", icon: FileText, label: "Reports" },
];

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-slate-950 text-slate-100">
        {/* Top nav */}
        <header className="sticky top-0 z-50 flex h-14 items-center gap-4 border-b border-slate-800 bg-slate-950/95 px-6 backdrop-blur">
          <span className="text-sm font-bold text-blue-400 tracking-tight">
            SEO Agent OS
          </span>
          <div className="ml-4 flex gap-1 text-sm">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-100 transition-colors"
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            ))}
          </div>
          <div className="ml-auto flex items-center gap-2">
            {/* Business selector */}
            <button className="flex items-center gap-1.5 rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-700 transition-colors">
              <Building2 className="h-3.5 w-3.5" />
              MTV Tech Solutions
              <ChevronDown className="h-3.5 w-3.5 text-slate-500" />
            </button>
            <button className="rounded-md p-1.5 text-slate-500 hover:bg-slate-800 hover:text-slate-300 transition-colors">
              <Settings className="h-4 w-4" />
            </button>
          </div>
        </header>

        {/* Main content */}
        <main className="min-h-[calc(100vh-3.5rem)]">{children}</main>
      </body>
    </html>
  );
}
