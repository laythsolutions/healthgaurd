/**
 * Public API client — no authentication required.
 * Used by public-facing pages for restaurant search, inspections, recalls, advisories.
 */

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function apiFetch<T>(path: string, params?: Record<string, string | number | undefined>): Promise<T> {
  const url = new URL(`${BASE}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== '') url.searchParams.set(k, String(v));
    });
  }
  const res = await fetch(url.toString(), {
    next: { revalidate: 60 },
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json();
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Restaurant {
  id: number;
  name: string;
  code: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  latitude: number | null;
  longitude: number | null;
  cuisine_type: string;
  current_grade: 'A' | 'B' | 'C' | 'P' | 'X' | '';
  last_inspection_date: string | null;
  last_inspection_score: number | null;
  compliance_score: number;
  status: 'ACTIVE' | 'SUSPENDED' | 'CLOSED';
}

export interface Violation {
  id: number;
  code: string;
  description: string;
  severity: 'critical' | 'serious' | 'minor' | 'observation';
  violation_status: string;
  category: string;
  points_deducted: number | null;
}

export interface Inspection {
  id: number;
  restaurant: number;
  restaurant_name: string;
  inspection_type: string;
  inspected_at: string;
  score: number | null;
  grade: string;
  passed: boolean | null;
  closed: boolean;
  source_jurisdiction: string;
  critical_violations: number;
  total_violations: number;
  violations?: Violation[];
}

export interface RecallProduct {
  id: number;
  product_description: string;
  brand_name: string;
  upc_codes: string[];
  lot_numbers: string[];
  best_by_dates: string[];
  package_sizes: string[];
  code_info: string;
}

export interface Recall {
  id: number;
  source: 'fda' | 'usda_fsis' | 'cdc' | 'manual';
  external_id: string;
  title: string;
  reason: string;
  hazard_type: string;
  classification: 'I' | 'II' | 'III' | '';
  status: 'active' | 'completed' | 'terminated' | 'ongoing';
  recalling_firm: string;
  firm_state: string;
  recall_initiation_date: string | null;
  affected_states: string[];
  product_count?: number;
  products?: RecallProduct[];
}

export interface PaginatedResult<T> {
  total: number;
  offset: number;
  results: T[];
}

// ---------------------------------------------------------------------------
// Restaurant endpoints
// ---------------------------------------------------------------------------

export async function searchRestaurants(params: {
  q?: string;
  city?: string;
  state?: string;
  grade?: string;
  page_size?: number;
  offset?: number;
}): Promise<PaginatedResult<Restaurant>> {
  return apiFetch('/api/v1/public/restaurants/', {
    search: params.q,
    city: params.city,
    state: params.state,
    grade: params.grade,
    page_size: params.page_size ?? 20,
    offset: params.offset ?? 0,
  });
}

export async function getRestaurant(id: string | number): Promise<Restaurant> {
  return apiFetch(`/api/v1/public/restaurants/${id}/`);
}

export async function getRestaurantInspections(restaurantId: string | number, limit = 10): Promise<Inspection[]> {
  return apiFetch(`/api/v1/inspections/restaurant/${restaurantId}/`, { limit });
}

// ---------------------------------------------------------------------------
// Inspections
// ---------------------------------------------------------------------------

export async function getInspection(id: string | number): Promise<Inspection> {
  return apiFetch(`/api/v1/inspections/${id}/`);
}

// ---------------------------------------------------------------------------
// Recalls
// ---------------------------------------------------------------------------

export async function getRecalls(params: {
  status?: string;
  hazard?: string;
  state?: string;
  source?: string;
  search?: string;
  page_size?: number;
  offset?: number;
}): Promise<PaginatedResult<Recall>> {
  return apiFetch('/api/v1/recalls/', {
    status: params.status ?? 'active',
    hazard: params.hazard,
    state: params.state,
    source: params.source,
    search: params.search,
    page_size: params.page_size ?? 20,
    offset: params.offset ?? 0,
  });
}

export async function getRecall(id: string | number): Promise<Recall> {
  return apiFetch(`/api/v1/recalls/${id}/`);
}
