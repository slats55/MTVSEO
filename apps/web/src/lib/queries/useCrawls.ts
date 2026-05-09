import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api/client";
import { API_ROUTES } from "@/lib/api/routes";
import type { CrawlListResponse } from "@/lib/api/types/crawls";

const QUERY_KEY = ["crawls", "list"] as const;

export function useCrawls() {
  return useQuery<CrawlListResponse>({
    queryKey: QUERY_KEY,
    queryFn: () =>
      apiGet<CrawlListResponse>(`${API_ROUTES.CRAWLS}?limit=4&skip=0`),
  });
}