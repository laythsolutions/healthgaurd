/**
 * Mobile-optimized restaurant grade card — linked from a QR code posted at
 * the establishment entrance.
 *
 * URL: /qr/{restaurant_id}
 *
 * The page is intentionally minimal and fast-loading:
 *   - No JS frameworks beyond React server components
 *   - Grade letter displayed in a huge, readable font
 *   - Loads critical inspection data only
 *   - Works on 3G connections (no heavy assets)
 */

import { notFound } from "next/navigation";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface RestaurantData {
  id: number;
  name: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  current_grade: string;
  last_inspection_date: string | null;
  last_inspection_score: number | null;
  compliance_score: number;
  health_department_id: string;
}

interface Inspection {
  id: number;
  inspected_at: string;
  grade: string;
  score: number | null;
  inspection_type: string;
  violations: Violation[];
}

interface Violation {
  id: number;
  description: string;
  severity: string;
  violation_status: string;
}

async function getRestaurant(id: string): Promise<RestaurantData | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/public/restaurants/${id}/`, {
      next: { revalidate: 300 },  // cache 5 min
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

async function getInspections(restaurantId: string): Promise<Inspection[]> {
  try {
    const res = await fetch(
      `${API_BASE}/api/v1/inspections/restaurant/${restaurantId}/`,
      { next: { revalidate: 300 } },
    );
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

// ---------------------------------------------------------------------------
// Grade display helpers
// ---------------------------------------------------------------------------

const GRADE_CONFIG: Record<string, { bg: string; text: string; label: string; emoji: string }> = {
  A: { bg: "bg-emerald-500", text: "text-white",    label: "Excellent",  emoji: "✓" },
  B: { bg: "bg-amber-400",   text: "text-black",    label: "Good",       emoji: "✓" },
  C: { bg: "bg-orange-500",  text: "text-white",    label: "Adequate",   emoji: "!" },
  P: { bg: "bg-blue-500",    text: "text-white",    label: "Conditional pass", emoji: "~" },
  X: { bg: "bg-red-600",     text: "text-white",    label: "Closed",     emoji: "✗" },
};

const SEVERITY_COLOR: Record<string, string> = {
  critical:    "text-red-400 bg-red-950/50 border-red-800/40",
  serious:     "text-orange-400 bg-orange-950/50 border-orange-800/40",
  major:       "text-amber-400 bg-amber-950/50 border-amber-800/40",
  minor:       "text-slate-400 bg-slate-800/50 border-slate-700/40",
  observation: "text-slate-500 bg-slate-900/50 border-slate-800/40",
};

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default async function QRPage({
  params,
}: {
  params: { id: string };
}) {
  const [restaurant, inspections] = await Promise.all([
    getRestaurant(params.id),
    getInspections(params.id),
  ]);

  if (!restaurant) notFound();

  const grade   = restaurant.current_grade?.toUpperCase() || "?";
  const cfg     = GRADE_CONFIG[grade] ?? { bg: "bg-slate-700", text: "text-white", label: "Unknown", emoji: "?" };
  const latest  = inspections[0] ?? null;
  const criticals = latest?.violations?.filter(v => v.severity === "critical") ?? [];

  const lastInspectedLabel = restaurant.last_inspection_date
    ? new Date(restaurant.last_inspection_date).toLocaleDateString("en-US", {
        month: "long", day: "numeric", year: "numeric",
      })
    : "Not on record";

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col items-center px-4 py-8 max-w-sm mx-auto">

      {/* Header */}
      <div className="w-full mb-6 text-center">
        <p className="text-xs text-slate-500 uppercase tracking-widest mb-1">Health Inspection Grade</p>
        <h1 className="text-xl font-bold text-white leading-tight">{restaurant.name}</h1>
        <p className="text-sm text-slate-400 mt-0.5">{restaurant.address}, {restaurant.city}, {restaurant.state}</p>
      </div>

      {/* Grade block */}
      <div className={`w-48 h-48 rounded-3xl ${cfg.bg} flex flex-col items-center justify-center shadow-2xl mb-4`}>
        <span className={`text-8xl font-black ${cfg.text} leading-none`}>{grade}</span>
        <span className={`text-sm font-medium ${cfg.text} opacity-80 mt-1`}>{cfg.label}</span>
      </div>

      {/* Score pill */}
      {restaurant.last_inspection_score !== null && (
        <div className="mb-6 px-4 py-1.5 rounded-full bg-slate-800 border border-slate-700 text-sm text-slate-300">
          Score: <span className="font-semibold text-white">{restaurant.last_inspection_score}</span> / 100
        </div>
      )}

      {/* Last inspection */}
      <div className="w-full bg-slate-900 border border-slate-800 rounded-2xl p-4 mb-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-slate-500">Last inspected</span>
          <span className="text-white font-medium">{lastInspectedLabel}</span>
        </div>
        {latest?.inspection_type && (
          <div className="flex justify-between text-sm">
            <span className="text-slate-500">Type</span>
            <span className="text-white capitalize">{latest.inspection_type.replace("_", " ")}</span>
          </div>
        )}
        {restaurant.health_department_id && (
          <div className="flex justify-between text-sm">
            <span className="text-slate-500">Health dept ID</span>
            <span className="text-slate-300 font-mono text-xs">{restaurant.health_department_id}</span>
          </div>
        )}
      </div>

      {/* Critical violations */}
      {criticals.length > 0 && (
        <div className="w-full mb-4">
          <p className="text-xs font-semibold text-red-400 uppercase tracking-wider mb-2">
            Critical violations from last inspection
          </p>
          <ul className="space-y-2">
            {criticals.map(v => (
              <li
                key={v.id}
                className={`text-sm px-3 py-2 rounded-lg border ${SEVERITY_COLOR.critical}`}
              >
                {v.description}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* All-clear when no criticals */}
      {criticals.length === 0 && latest && (
        <div className="w-full mb-4 px-4 py-3 rounded-xl bg-emerald-950/40 border border-emerald-800/30 text-sm text-emerald-400 text-center">
          No critical violations on record for the latest inspection.
        </div>
      )}

      {/* Older violations notice */}
      {latest && (latest.violations?.length ?? 0) > criticals.length && (
        <p className="text-xs text-slate-600 mb-4 text-center">
          {(latest.violations.length - criticals.length)} non-critical violation{latest.violations.length - criticals.length !== 1 ? "s" : ""} not shown.
        </p>
      )}

      {/* Grade history chips */}
      {inspections.length > 1 && (
        <div className="w-full mb-6">
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Grade history</p>
          <div className="flex flex-wrap gap-2">
            {inspections.slice(0, 6).map(ins => {
              const g = ins.grade?.toUpperCase() || "?";
              const c = GRADE_CONFIG[g] ?? { bg: "bg-slate-700", text: "text-white" };
              return (
                <div key={ins.id} className={`${c.bg} ${c.text} text-xs px-3 py-1.5 rounded-lg font-bold`}>
                  {g}
                  <span className="font-normal opacity-70 ml-1">
                    {new Date(ins.inspected_at).toLocaleDateString("en-US", { month: "short", year: "2-digit" })}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Full history link */}
      <Link
        href={`/restaurant/${restaurant.id}`}
        className="w-full text-center py-3 rounded-xl border border-slate-700 text-sm text-slate-300 hover:text-white hover:border-slate-500 transition-colors mb-8"
      >
        View full inspection history
      </Link>

      {/* Footer */}
      <div className="text-center space-y-1">
        <p className="text-xs text-slate-600">
          Data sourced from public health department records.
        </p>
        <p className="text-xs text-slate-700">
          Grades reflect the most recent routine inspection only.
        </p>
      </div>
    </div>
  );
}

export async function generateMetadata({ params }: { params: { id: string } }) {
  const restaurant = await getRestaurant(params.id);
  if (!restaurant) return { title: "Restaurant Not Found" };
  return {
    title: `${restaurant.name} — Health Grade ${restaurant.current_grade || "?"}`,
    description: `Health inspection grade for ${restaurant.name} in ${restaurant.city}, ${restaurant.state}.`,
  };
}
