/**
 * Authenticated API client for the Health Department Portal.
 * Reads the JWT access token from localStorage (key: "hd_access").
 */

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('hd_access');
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  params?: Record<string, string | number | undefined>,
): Promise<T> {
  const url = new URL(`${BASE}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== '') url.searchParams.set(k, String(v));
    });
  }

  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string> ?? {}),
  };

  const res = await fetch(url.toString(), { ...options, headers });
  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('hd_access');
      window.location.href = '/login';
    }
    throw new Error('Unauthorized');
  }
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json();
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ScheduledInspection {
  id: number;
  restaurant: number;
  restaurant_name: string;
  restaurant_address: string;
  restaurant_city: string;
  restaurant_state: string;
  scheduled_date: string;
  scheduled_time: string | null;
  inspection_type: string;
  assigned_inspector_id: string;
  jurisdiction: string;
  notes: string;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'missed';
  completed_inspection: number | null;
}

export interface RecallAcknowledgment {
  id: number;
  recall: number;
  recall_title?: string;
  recall_classification?: string;
  recall_hazard_type?: string;
  restaurant: number;
  restaurant_name?: string;
  status: 'pending' | 'acknowledged' | 'not_affected' | 'remediated' | 'escalated';
  notes: string;
  remediation_date: string | null;
  units_removed: number | null;
  created_at: string;
  updated_at: string;
}

export interface OutbreakInvestigation {
  id: number;
  title: string;
  pathogen: string;
  status: 'open' | 'closed' | 'monitoring';
  opened_at: string;
  closed_at: string | null;
  case_count_at_open: number;
  cluster_score: number | null;
  geographic_scope: string;
  auto_generated: boolean;
}

export interface PaginatedResult<T> {
  total: number;
  offset: number;
  results: T[];
}

export interface PortalStats {
  scheduled_this_week: number;
  overdue_inspections: number;
  active_recalls: number;
  open_investigations: number;
  pending_acknowledgments: number;
}

// ---------------------------------------------------------------------------
// Inspection schedules
// ---------------------------------------------------------------------------

export async function getScheduledInspections(params?: {
  status?: string;
  since?: string;
  until?: string;
  jurisdiction?: string;
  page_size?: number;
  offset?: number;
}): Promise<PaginatedResult<ScheduledInspection>> {
  return apiFetch('/api/v1/inspections/schedule/', {}, {
    status: params?.status,
    since: params?.since,
    until: params?.until,
    jurisdiction: params?.jurisdiction,
    page_size: params?.page_size ?? 50,
    offset: params?.offset ?? 0,
  });
}

export async function createScheduledInspection(
  data: Partial<ScheduledInspection>,
): Promise<ScheduledInspection> {
  return apiFetch('/api/v1/inspections/schedule/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateScheduledInspection(
  id: number,
  data: Partial<ScheduledInspection>,
): Promise<ScheduledInspection> {
  return apiFetch(`/api/v1/inspections/schedule/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// ---------------------------------------------------------------------------
// Recall acknowledgments
// ---------------------------------------------------------------------------

export async function getAcknowledgments(params?: {
  status?: string;
}): Promise<RecallAcknowledgment[]> {
  return apiFetch('/api/v1/recalls/acknowledgments/', {}, {
    status: params?.status,
  });
}

export async function updateAcknowledgment(
  id: number,
  data: Partial<RecallAcknowledgment>,
): Promise<RecallAcknowledgment> {
  return apiFetch(`/api/v1/recalls/acknowledgments/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// ---------------------------------------------------------------------------
// Outbreak investigations
// ---------------------------------------------------------------------------

export async function getInvestigations(params?: {
  status?: string;
}): Promise<OutbreakInvestigation[]> {
  return apiFetch('/api/v1/clinical/investigations/', {}, {
    status: params?.status,
  });
}

export async function updateInvestigation(
  id: number,
  data: Partial<OutbreakInvestigation>,
): Promise<OutbreakInvestigation> {
  return apiFetch(`/api/v1/clinical/investigations/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}
