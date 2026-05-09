import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api/client";
import { API_ROUTES } from "@/lib/api/routes";
import type { BusinessListResponse } from "@/lib/api/types/businesses";

const QUERY_KEY = ["businesses", "list"] as const;

export function useBusinesses() {
  return useQuery<BusinessListResponse>({
    queryKey: QUERY_KEY,
    queryFn: () => apiGet<BusinessListResponse>(API_ROUTES.BUSINESSES),
  });
}
