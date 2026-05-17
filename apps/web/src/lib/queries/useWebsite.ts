import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api/client";
import { API_ROUTES } from "@/lib/api/routes";
import type { Website } from "@/lib/api/types/websites";

const QUERY_KEY = ["websites", "detail"] as const;

export function useWebsite(id: string) {
  return useQuery<Website>({
    queryKey: [...QUERY_KEY, id],
    queryFn: () => apiGet<Website>(API_ROUTES.WEBSITE_BY_ID(id)),
    enabled: !!id,
  });
}