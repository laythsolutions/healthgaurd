/**
 * Medical institution API client.
 *
 * Authentication: X-Institution-Key header containing the raw institution key.
 * The key is stored in localStorage under "med_inst_key".
 */

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getKey(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("med_inst_key");
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const key = getKey();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (key) headers["X-Institution-Key"] = key;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("med_inst_key");
      window.location.href = "/medical/login";
    }
    throw new Error("Institution key invalid or expired.");
  }

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }

  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface CaseSubmission {
  patient_id: string;       // will be anonymized server-side — never stored
  age: number;
  sex?: "M" | "F" | "O";
  lat: number;
  lon: number;
  zip_code: string;
  onset_date: string;       // YYYY-MM-DD
  symptoms: string[];
  pathogen?: string;
  illness_status?: "suspected" | "confirmed" | "ruled_out";
  outcome?: string;
  hospitalized?: boolean;
  notes?: string;
  exposures?: ExposureInput[];
}

export interface ExposureInput {
  exposure_type: string;
  exposure_date?: string;
  geohash?: string;
  establishment_type?: string;
  food_items?: string[];
  notes?: string;
}

export interface SubmittedCase {
  id: number;
  subject_hash: string;
  age_range: string;
  geohash: string;
  zip3: string;
  onset_date: string;
  symptoms: string[];
  pathogen: string;
  illness_status: string;
  outcome: string;
  created_at: string;
}

export interface ClusterAlert {
  id: number;
  title: string;
  status: string;
  pathogen: string;
  geographic_scope: string;
  cluster_start_date: string | null;
  cluster_end_date: string | null;
  case_count_at_open: number;
  cluster_score: number | null;
  auto_generated: boolean;
  opened_at: string;
}

export interface MedicalPortalStats {
  cases_submitted_30d: number;
  cases_this_week: number;
  open_cluster_alerts: number;
  confirmed_cases: number;
}

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------

export async function submitCase(payload: CaseSubmission): Promise<SubmittedCase> {
  return request<SubmittedCase>("/api/v1/clinical/cases/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getRecentCases(
  limit = 20,
  offset = 0,
): Promise<{ total: number; offset: number; results: SubmittedCase[] }> {
  return request(`/api/v1/clinical/cases/?page_size=${limit}&offset=${offset}`);
}

export async function getClusterAlerts(status?: string): Promise<ClusterAlert[]> {
  const qs = status ? `?status=${status}` : "?status=open&status=active";
  return request<ClusterAlert[]>(`/api/v1/clinical/investigations/${qs}`);
}

/** Verify an institution key by hitting the cases list endpoint. */
export async function verifyInstitutionKey(key: string): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/api/v1/clinical/cases/`, {
      headers: {
        "Content-Type": "application/json",
        "X-Institution-Key": key,
      },
    });
    return res.status !== 401;
  } catch {
    return false;
  }
}
