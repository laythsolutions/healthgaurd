'use client';

import { useEffect, useState } from 'react';
import {
  Activity,
  FlaskConical,
  MapPin,
  Calendar,
  CheckCircle2,
  Lock,
} from 'lucide-react';
import {
  getInvestigations,
  updateInvestigation,
  type OutbreakInvestigation,
} from '@/lib/health-dept-api';

const STATUS_COLORS: Record<string, { dot: string; text: string; bg: string; border: string }> = {
  open:       { dot: 'bg-red-400 animate-pulse', text: 'text-red-700',     bg: 'bg-red-50',     border: 'border-red-100' },
  monitoring: { dot: 'bg-amber-400',             text: 'text-amber-700',   bg: 'bg-amber-50',   border: 'border-amber-100' },
  closed:     { dot: 'bg-gray-300',              text: 'text-gray-500',    bg: 'bg-gray-50',    border: 'border-gray-100' },
};

export default function ClustersPage() {
  const [investigations, setInvestigations] = useState<OutbreakInvestigation[]>([]);
  const [filter, setFilter] = useState('open');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const data = await getInvestigations({ status: filter || undefined });
        setInvestigations(Array.isArray(data) ? data : []);
      } catch {
        setError('Could not load outbreak investigations.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [filter]);

  async function transition(id: number, newStatus: string) {
    setUpdatingId(id);
    try {
      const updated = await updateInvestigation(id, { status: newStatus as OutbreakInvestigation['status'] });
      setInvestigations((prev) => prev.map((i) => (i.id === id ? updated : i)));
    } catch {
      setError('Failed to update investigation status.');
    } finally {
      setUpdatingId(null);
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-black text-gray-900 flex items-center gap-2">
          <Activity className="h-6 w-6 text-red-500" />
          Outbreak Clusters
        </h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Active and monitored foodborne illness outbreak investigations.
        </p>
      </div>

      {/* Privacy note */}
      <div className="mb-6 rounded-xl border border-amber-100 bg-amber-50 px-4 py-3 flex items-start gap-2 text-sm text-amber-700">
        <Lock className="h-4 w-4 mt-0.5 shrink-0" />
        <span>
          <strong>Restricted view.</strong> Cluster data is visible to health dept users only.
          No PII is displayed — all cases are anonymized at intake.
        </span>
      </div>

      {/* Status filter */}
      <div className="mb-6 flex gap-2 flex-wrap">
        {[
          { value: 'open',       label: 'Open' },
          { value: 'monitoring', label: 'Monitoring' },
          { value: 'closed',     label: 'Closed' },
          { value: '',           label: 'All' },
        ].map(({ value, label }) => (
          <button
            key={value}
            onClick={() => setFilter(value)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              filter === value
                ? 'bg-gray-900 text-white'
                : 'bg-white border text-gray-600 hover:border-gray-400'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-4 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-3 animate-pulse">
          {[...Array(3)].map((_, i) => <div key={i} className="h-32 rounded-2xl bg-gray-100" />)}
        </div>
      ) : investigations.length === 0 ? (
        <div className="rounded-2xl border bg-white shadow-sm py-16 text-center">
          <CheckCircle2 className="h-10 w-10 text-emerald-400 mx-auto mb-3" />
          <p className="font-medium text-gray-500">No {filter || ''} outbreak investigations.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {investigations.map((inv) => {
            const sc = STATUS_COLORS[inv.status] ?? STATUS_COLORS.open;
            return (
              <div key={inv.id} className={`rounded-2xl border p-5 ${sc.bg} ${sc.border}`}>
                {/* Header row */}
                <div className="flex items-start justify-between gap-4 flex-wrap mb-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${sc.text}`}>
                        <span className={`h-2 w-2 rounded-full ${sc.dot}`} />
                        {inv.status.charAt(0).toUpperCase() + inv.status.slice(1)}
                        {inv.auto_generated && (
                          <span className="ml-1 rounded-full bg-white/60 px-1.5 py-0.5 text-xs">
                            auto-generated
                          </span>
                        )}
                      </span>
                    </div>
                    <p className="font-bold text-gray-900">{inv.title}</p>
                  </div>

                  {/* Cluster score */}
                  {inv.cluster_score != null && (
                    <div className="shrink-0 text-right">
                      <p className="text-xs text-gray-500">Cluster score</p>
                      <p className={`text-2xl font-black ${sc.text}`}>
                        {Math.round(inv.cluster_score * 100)}
                      </p>
                    </div>
                  )}
                </div>

                {/* Meta row */}
                <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
                  {inv.pathogen && (
                    <span className="flex items-center gap-1.5">
                      <FlaskConical className="h-3.5 w-3.5" />
                      {inv.pathogen}
                    </span>
                  )}
                  {inv.geographic_scope && (
                    <span className="flex items-center gap-1.5">
                      <MapPin className="h-3.5 w-3.5" />
                      {inv.geographic_scope}
                    </span>
                  )}
                  <span className="flex items-center gap-1.5">
                    <Calendar className="h-3.5 w-3.5" />
                    Opened {new Date(inv.opened_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Activity className="h-3.5 w-3.5" />
                    {inv.case_count_at_open} cases
                  </span>
                </div>

                {/* Status actions */}
                <div className="flex flex-wrap gap-2">
                  {inv.status === 'open' && (
                    <>
                      <button
                        disabled={updatingId === inv.id}
                        onClick={() => transition(inv.id, 'monitoring')}
                        className="rounded-lg border border-amber-200 bg-white/70 px-3 py-1.5 text-xs font-medium text-amber-700 hover:bg-amber-100 disabled:opacity-50 transition-colors"
                      >
                        Move to monitoring
                      </button>
                      <button
                        disabled={updatingId === inv.id}
                        onClick={() => transition(inv.id, 'closed')}
                        className="rounded-lg border border-gray-200 bg-white/70 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-100 disabled:opacity-50 transition-colors"
                      >
                        Close investigation
                      </button>
                    </>
                  )}
                  {inv.status === 'monitoring' && (
                    <>
                      <button
                        disabled={updatingId === inv.id}
                        onClick={() => transition(inv.id, 'open')}
                        className="rounded-lg border border-red-200 bg-white/70 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100 disabled:opacity-50 transition-colors"
                      >
                        Re-escalate to open
                      </button>
                      <button
                        disabled={updatingId === inv.id}
                        onClick={() => transition(inv.id, 'closed')}
                        className="rounded-lg border border-gray-200 bg-white/70 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-100 disabled:opacity-50 transition-colors"
                      >
                        Close investigation
                      </button>
                    </>
                  )}
                  {inv.status === 'closed' && inv.closed_at && (
                    <p className="text-xs text-gray-400">
                      Closed {new Date(inv.closed_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Attribution */}
      <p className="mt-8 text-center text-xs text-gray-400 leading-relaxed">
        Outbreak investigations are generated from anonymized clinical case data.
        All case records are processed through the Privacy &amp; Anonymization Service
        before any cluster is surfaced here. Contact your supervisor for official
        public health communications.
      </p>
    </div>
  );
}
