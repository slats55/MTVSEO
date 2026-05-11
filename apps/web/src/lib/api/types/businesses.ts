// Business API types — aligned with backend BusinessRead / BusinessList schemas

export interface Business {
  id: string;
  user_id: string;
  name: string;
  website_url: string | null;
  description: string | null;
  business_type: string | null;
  location: string | null;
  phone: string | null;
  email: string | null;
  is_cannabis: boolean;
  is_ymyl: boolean;
  created_at: string;
  updated_at: string;
}

export interface BusinessListResponse {
  items: Business[];
  total: number;
}
