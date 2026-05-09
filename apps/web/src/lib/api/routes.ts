// API route paths — use these constants to avoid hardcoding strings
// Base: process.env.NEXT_PUBLIC_API_URL (default: http://localhost:8000)

export const API_ROUTES = {
  // Businesses
  BUSINESSES: "/api/v1/businesses/",
  BUSINESS_BY_ID: (id: string) => `/api/v1/businesses/${id}`,

  // Websites
  WEBSITES: "/api/v1/websites/",
  WEBSITE_BY_ID: (id: string) => `/api/v1/websites/${id}`,

  // Crawls
  CRAWLS: "/api/v1/crawls/",
  CRAWL_BY_ID: (id: string) => `/api/v1/crawls/${id}`,
  CRAWL_STATUS: (id: string) => `/api/v1/crawls/${id}/status`,
  CRAWL_CANCEL: (id: string) => `/api/v1/crawls/${id}/cancel`,

  // Pages
  PAGES: "/api/v1/pages/",
  PAGE_BY_ID: (id: string) => `/api/v1/pages/${id}`,
  PAGE_SUMMARY: (id: string) => `/api/v1/pages/summary/${id}`,
  PAGE_BY_URL: "/api/v1/pages/by-url/",
} as const;