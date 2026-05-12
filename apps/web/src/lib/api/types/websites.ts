// Website API types — aligned with backend WebsiteRead / WebsiteList schemas

export interface Website {
  id: string;
  business_id: string;
  url: string;
  name: string | null;
  created_at: string;
  updated_at: string;
}

export interface WebsiteListResponse {
  items: Website[];
  total: number;
}