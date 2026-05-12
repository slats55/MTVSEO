import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api/client";
import { API_ROUTES } from "@/lib/api/routes";
import type { SeoIssueListResponse } from "@/lib/api/types/seo_issues";

const QUERY_KEY = ["seo-issues", "list"] as const;

export function useSeoIssues() {
  return useQuery<SeoIssueListResponse>({
    queryKey: QUERY_KEY,
    queryFn: () => apiGet<SeoIssueListResponse>(`${API_ROUTES.SEO_ISSUES}?limit=4&skip=0`),
  });
}