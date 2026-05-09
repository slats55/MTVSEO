// Crawl API types — aligned with backend CrawlRunRead / CrawlRunList schemas

export type CrawlStatus = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED";

export interface CrawlRun {
  id: string;
  website_id: string;
  status: CrawlStatus;
  crawl_depth: number;
  max_pages: number;
  respect_robots: boolean;
  started_at: string | null;
  completed_at: string | null;
  pages_discovered: number;
  pages_crawled: number;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface CrawlListResponse {
  items: CrawlRun[];
  total: number;
}

// Map backend CrawlStatus to UI display labels
export const CRAWL_STATUS_LABELS: Record<CrawlStatus, string> = {
  PENDING: "Pending",
  RUNNING: "Running",
  COMPLETED: "Completed",
  FAILED: "Failed",
  CANCELLED: "Cancelled",
} as const;

// Map backend CrawlStatus to StatusBadge variant
export const CRAWL_STATUS_VARIANTS: Record<CrawlStatus, "success" | "warning" | "error" | "info" | "neutral"> = {
  PENDING: "neutral",
  RUNNING: "info",
  COMPLETED: "success",
  FAILED: "error",
  CANCELLED: "neutral",
} as const;