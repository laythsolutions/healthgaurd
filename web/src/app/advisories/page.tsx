import { Activity, Lock, MapPin, Calendar, FlaskConical, TriangleAlert, ShieldCheck } from 'lucide-react';
import { PublicNav } from '@/components/public/nav';
import { PublicFooter } from '@/components/public/footer';

export const metadata = {
  title: 'Outbreak Advisories — [PROJECT_NAME]',
  description: 'Anonymized, aggregated foodborne illness outbreak advisories from participating health departments.',
  // Revalidate every 5 minutes to match server-side cache
  other: { 'Cache-Control': 'public, max-age=300' },
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

interface Advisory {
  id: number;
  title: string;
  status: string;
  pathogen: string;
  suspected_vehicle: string;
  geographic_scope: string;
  cluster_start_date: string | null;
  cluster_end_date: string | null;
  case_count: number;
  cluster_score: number | null;
  auto_generated: boolean;
  opened_at: string;
}

// ---------------------------------------------------------------------------
// Data fetching (Server Component)
// ---------------------------------------------------------------------------

async function getAdvisories(): Promise<Advisory[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/public/advisories/?limit=50`, {
      next: { revalidate: 300 },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results ?? [];
  } catch {
    return [];
  }
}

// ---------------------------------------------------------------------------
// UI helpers
// ---------------------------------------------------------------------------

const STATUS_CONFIG: Record<string, { label: string; dot: string; text: string; border: string }> = {
  open:     { label: 'Under investigation', dot: 'bg-amber-400 animate-pulse', text: 'text-amber-700', border: 'border-amber-100' },
  active:   { label: 'Active investigation', dot: 'bg-red-500 animate-pulse',  text: 'text-red-700',   border: 'border-red-100' },
  closed:   { label: 'Closed',              dot: 'bg-gray-300',                text: 'text-gray-500',  border: 'border-gray-100' },
  archived: { label: 'Archived',            dot: 'bg-gray-200',                text: 'text-gray-400',  border: 'border-gray-100' },
};

function ScorePill({ score }: { score: number | null }) {
  if (!score) return null;
  const color =
    score >= 35 ? 'bg-red-50 text-red-700 border-red-200' :
    score >= 20 ? 'bg-amber-50 text-amber-700 border-amber-200' :
                  'bg-gray-50 text-gray-500 border-gray-200';
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-mono ${color}`}>
      score {score.toFixed(1)}
    </span>
  );
}

function GeohashCell({ scope }: { scope: string }) {
  // Extract geohash prefix from "Geohash cell XXXX (STATE)" pattern
  const match = scope.match(/([0-9a-z]{4,6})/i);
  const code = match ? match[1].toUpperCase() : null;
  if (!code) return <span className="text-gray-600">{scope}</span>;
  return (
    <span className="inline-flex items-center gap-1.5 text-gray-600">
      <span
        className="inline-block w-3 h-3 rounded-sm"
        style={{ background: `hsl(${(code.charCodeAt(0) * 37) % 360},60%,55%)` }}
        title={`Geohash cell ${code}`}
      />
      {scope}
    </span>
  );
}

function AdvisoryCard({ adv }: { adv: Advisory }) {
  const sc = STATUS_CONFIG[adv.status] ?? STATUS_CONFIG.open;
  const dateLabel = adv.cluster_start_date
    ? new Date(adv.cluster_start_date).toLocaleDateString('en-US', {
        month: 'long', day: 'numeric', year: 'numeric',
      })
    : null;
  const endLabel = adv.cluster_end_date
    ? new Date(adv.cluster_end_date).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric',
      })
    : null;

  return (
    <article className={`rounded-2xl border bg-white shadow-sm p-6 ${sc.border}`}>
      {/* Status + pathogen row */}
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <span className="flex items-center gap-1.5 text-xs font-medium">
          <span className={`h-2 w-2 rounded-full ${sc.dot}`} />
          <span className={sc.text}>{sc.label}</span>
        </span>

        {adv.pathogen && (
          <span className="inline-flex items-center gap-1 rounded-full bg-red-50 px-2.5 py-0.5 text-xs font-semibold text-red-700 border border-red-100">
            <FlaskConical className="h-3 w-3" />
            {adv.pathogen}
          </span>
        )}

        {adv.auto_generated && (
          <span className="rounded-full bg-slate-50 px-2 py-0.5 text-xs text-slate-400 border border-slate-100">
            auto-detected
          </span>
        )}

        <ScorePill score={adv.cluster_score} />
      </div>

      <h2 className="font-bold text-gray-900 text-base leading-snug mb-3">{adv.title}</h2>

      {/* Meta row */}
      <div className="flex flex-wrap gap-x-5 gap-y-1 text-sm text-gray-500 mb-3">
        <span className="flex items-center gap-1.5">
          <MapPin className="h-3.5 w-3.5 flex-shrink-0" />
          <GeohashCell scope={adv.geographic_scope} />
        </span>

        {dateLabel && (
          <span className="flex items-center gap-1.5">
            <Calendar className="h-3.5 w-3.5" />
            Since {dateLabel}
            {endLabel && adv.status === 'closed' && ` — ${endLabel}`}
          </span>
        )}

        <span className="flex items-center gap-1.5">
          <Activity className="h-3.5 w-3.5" />
          {adv.case_count} case{adv.case_count !== 1 ? 's' : ''}
        </span>
      </div>

      {adv.suspected_vehicle && (
        <div className="rounded-lg bg-gray-50 px-3 py-2 text-xs text-gray-600 border border-gray-100">
          <strong>Suspected vehicle:</strong> {adv.suspected_vehicle}
        </div>
      )}
    </article>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default async function AdvisoriesPage() {
  const advisories = await getAdvisories();

  const active   = advisories.filter(a => a.status === 'active');
  const open     = advisories.filter(a => a.status === 'open');
  const resolved = advisories.filter(a => !['active', 'open'].includes(a.status));

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <PublicNav />

      <main className="mx-auto w-full max-w-4xl flex-1 px-4 sm:px-6 py-8">

        {/* Header */}
        <div className="mb-6 flex items-center gap-2">
          <Activity className="h-5 w-5 text-amber-500" />
          <h1 className="text-2xl font-black text-gray-900">Outbreak Advisories</h1>
          {advisories.length > 0 && (
            <span className="ml-2 rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-700">
              {advisories.length} advisory{advisories.length !== 1 ? 'ies' : ''}
            </span>
          )}
        </div>

        {/* Privacy notice */}
        <div className="mb-6 rounded-xl border border-amber-100 bg-amber-50 p-4 flex items-start gap-3">
          <Lock className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
          <div className="text-sm text-amber-700 leading-relaxed">
            <strong>Privacy by design.</strong> All advisories are derived from anonymized,
            aggregated case data submitted by participating healthcare institutions.
            No personally identifiable information is published. Location precision is
            limited to ~40 km geographic cells. Only investigations with {'\u2265'}3 confirmed
            or probable cases are shown.
          </div>
        </div>

        {/* No advisories */}
        {advisories.length === 0 && (
          <div className="rounded-2xl border border-green-100 bg-green-50 p-8 text-center">
            <ShieldCheck className="h-10 w-10 text-green-500 mx-auto mb-3" />
            <h2 className="text-lg font-bold text-green-800 mb-1">No active advisories</h2>
            <p className="text-sm text-green-700">
              No outbreak investigations currently meet the public disclosure threshold.
              This page updates automatically as new cases are reported and investigated.
            </p>
          </div>
        )}

        {/* Active investigations — highest priority */}
        {active.length > 0 && (
          <section className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <TriangleAlert className="h-4 w-4 text-red-500" />
              <h2 className="font-bold text-gray-900 text-sm uppercase tracking-wider">
                Active Investigations
              </h2>
            </div>
            <div className="space-y-4">
              {active.map(adv => <AdvisoryCard key={adv.id} adv={adv} />)}
            </div>
          </section>
        )}

        {/* Open (under investigation) */}
        {open.length > 0 && (
          <section className="mb-8">
            <h2 className="font-bold text-gray-700 text-sm uppercase tracking-wider mb-4">
              Under Investigation
            </h2>
            <div className="space-y-4">
              {open.map(adv => <AdvisoryCard key={adv.id} adv={adv} />)}
            </div>
          </section>
        )}

        {/* Resolved */}
        {resolved.length > 0 && (
          <section>
            <h2 className="font-bold text-gray-400 text-sm uppercase tracking-wider mb-4">
              Resolved
            </h2>
            <div className="space-y-4 opacity-75">
              {resolved.map(adv => <AdvisoryCard key={adv.id} adv={adv} />)}
            </div>
          </section>
        )}

        {/* Attribution */}
        <div className="mt-10 rounded-xl border border-gray-100 bg-white p-5 text-xs text-gray-400 leading-relaxed">
          <strong className="text-gray-500">Data sources &amp; methodology:</strong> Advisories
          are generated automatically by the spatial-temporal clustering engine when ≥3 cases
          share a pathogen, geographic cell, and a 30-day onset window. All case data is
          processed through the Privacy &amp; Anonymization Service before any aggregated
          advisory is published. For official outbreak communications, contact your local or
          state health department.
        </div>
      </main>

      <PublicFooter />
    </div>
  );
}
