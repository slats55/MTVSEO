import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPost, type ApiError } from "@/lib/api/client";
import { API_ROUTES } from "@/lib/api/routes";
import type { CrawlListResponse, CrawlRun } from "@/lib/api/types/crawls";

const QUERY_KEY = ["crawls", "list"] as const;

export function useCrawls() {
  return useQuery<CrawlListResponse>({
    queryKey: QUERY_KEY,
    queryFn: () =>
      apiGet<CrawlListResponse>(`${API_ROUTES.CRAWLS}?limit=4&skip=0`),
  });
}

export interface CreateCrawlPayload {
  website_id: string;
  crawl_depth?: number;
  max_pages?: number;
  respect_robots?: boolean;
}

const CREATE_MUTATION_KEY = ["crawls", "create"] as const;

export function useCreateCrawl() {
  const queryClient = useQueryClient();

  return useMutation<CrawlRun, ApiError, CreateCrawlPayload>({
    mutationKey: CREATE_MUTATION_KEY,
    mutationFn: (payload) =>
      apiPost<CrawlRun>(API_ROUTES.CRAWLS, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}