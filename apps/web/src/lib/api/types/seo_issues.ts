// SEO Issue types — aligned with backend SeoIssue model

export type IssueSeverity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";

export interface SeoIssue {
  id: string;
  page_id: string | null;
  crawl_run_id: string;
  issue_type: string;
  severity: IssueSeverity;
  title: string;
  description: string | null;
  recommendation: string | null;
  affected_element: string | null;
  created_at: string;
  updated_at: string;
}

export interface SeoIssueListResponse {
  items: SeoIssue[];
  total: number;
}

// Map backend IssueSeverity to UI display labels
export const SEVERITY_LABELS: Record<IssueSeverity, string> = {
  CRITICAL: "Critical",
  HIGH: "High",
  MEDIUM: "Medium",
  LOW: "Low",
  INFO: "Info",
} as const;

// Map IssueSeverity to StatusBadge variant
export const SEVERITY_VARIANTS: Record<IssueSeverity, "error" | "warning" | "info" | "neutral"> = {
  CRITICAL: "error",
  HIGH: "error",
  MEDIUM: "warning",
  LOW: "info",
  INFO: "neutral",
} as const;