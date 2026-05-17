import { useQuery } from "@tanstack/react-query";
import { apiGet, type ApiError } from "@/lib/api/client";
import { API_ROUTES } from "@/lib/api/routes";
import type { CrawlListResponse } from "@/lib/api/types/crawls";

export function useWebsiteCrawls(websiteId: string) {
  return useQuery<CrawlListResponse, ApiError>({
    queryKey: ["crawls", "website", websiteId],
    queryFn: () =>
      apiGet<CrawlListResponse>(
        `${API_ROUTES.CRAWLS}?website_id=${websiteId}&limit=10&skip=0`
      ),
    // Only run when we have a real websiteId
    enabled: Boolean(websiteId),
  });
}