export interface Company {
  id: string;
  name: string;
  category: string;
  city: string;
  address: string | null;
  rating: number | null;
  reviews_count: number;
  site: string | null;
  phone: string | null;
  source: string;
  created_at: string;
  updated_at: string;
}

export interface CompaniesResponse {
  companies: Company[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface SearchParams {
  search?: string;
  city?: string;
  page?: number;
  pageSize?: number;
}