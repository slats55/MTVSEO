import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api/client";
import { API_ROUTES } from "@/lib/api/routes";
import type { SeoIssueListResponse } from "@/lib/api/types/seo_issues";

export interface UseSeoIssuesParams {
  crawlRunId?: string;
  skip?: number;
  limit?: number;
  pageId?: string;
}

const DEFAULT_LIMIT = 20;

function buildUrl(params: UseSeoIssuesParams): string {
  const qs = new URLSearchParams();
  if (params.crawlRunId) qs.set("crawl_run_id", params.crawlRunId);
  if (params.pageId) qs.set("page_id", params.pageId);
  const skip = params.skip ?? 0;
  const limit = params.limit ?? DEFAULT_LIMIT;
  qs.set("skip", String(skip));
  qs.set("limit", String(limit));
  return `${API_ROUTES.SEO_ISSUES}?${qs.toString()}`;
}

export function useSeoIssues(params: UseSeoIssuesParams = {}) {
  const queryKey = ["seo-issues", "list", params] as const;
  return useQuery<SeoIssueListResponse>({
    queryKey,
    queryFn: () => apiGet<SeoIssueListResponse>(buildUrl(params)),
  });
}
