import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api/client";
import { API_ROUTES } from "@/lib/api/routes";
import type { WebsiteListResponse } from "@/lib/api/types/websites";

const QUERY_KEY = ["websites", "list"] as const;

export function useWebsites() {
  return useQuery<WebsiteListResponse>({
    queryKey: QUERY_KEY,
    queryFn: () => apiGet<WebsiteListResponse>(`${API_ROUTES.WEBSITES}?limit=4&skip=0`),
  });
}