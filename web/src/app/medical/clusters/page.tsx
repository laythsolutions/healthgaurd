"use client";

import { useEffect, useState } from "react";
import { getClusterAlerts, type ClusterAlert } from "@/lib/medical-api";

const STATUS_FILTERS = [
  { value: "",        label: "All" },
  { value: "open",    label: "Open" },
  { value: "active",  label: "Active" },
  { value: "closed",  label: "Closed" },
];

function ScoreBadge({ score }: { score: number | null }) {
  if (score === null || score === undefined) return null;
  const color =
    score >= 35 ? "bg-red-900/40 border-red-700/30 text-red-300" :
    score >= 20 ? "bg-amber-900/30 border-amber-700/30 text-amber-300" :
                  "bg-slate-800 border-slate-700 text-slate-400";
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border font-mono ${color}`}>
      {score.toFixed(1)}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const cfg: Record<string, string> = {
    open:     "bg-blue-900/30 border-blue-700/30 text-blue-300",
    active:   "bg-amber-900/30 border-amber-700/30 text-amber-300",
    closed:   "bg-slate-800 border-slate-700 text-slate-500",
    archived: "bg-slate-800 border-slate-700 text-slate-600",
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border capitalize ${cfg[status] ?? cfg.closed}`}>
      {status}
    </span>
  );
}

export default function ClustersPage() {
  const [alerts, setAlerts] = useState<ClusterAlert[]>([]);
  const [status, setStatus] = useState("open");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    getClusterAlerts(status || undefined)
      .then(setAlerts)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [status]);

  const highPriority = alerts.filter(a => (a.cluster_score ?? 0) >= 35);
  const rest         = alerts.filter(a => (a.cluster_score ?? 0) < 35);

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white">Cluster Alerts</h1>
        <p className="text-sm text-slate-400 mt-0.5">
          Auto-detected spatial-temporal outbreak clusters from anonymized case data
        </p>
      </div>

      {/* Privacy reminder */}
      <div className="bg-slate-900/60 border border-slate-700/40 rounded-xl px-4 py-3 flex gap-3">
        <svg className="w-4 h-4 text-slate-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
        </svg>
        <p className="text-xs text-slate-500 leading-relaxed">
          Cluster locations are displayed at geohash precision-4 (~40 km cells). No patient
          identifiers are shown. Case counts are aggregated totals only.
        </p>
      </div>

      {/* Status filters */}
      <div className="flex gap-2 flex-wrap">
        {STATUS_FILTERS.map(f => (
          <button
            key={f.value}
            onClick={() => setStatus(f.value)}
            className={`px-4 py-1.5 rounded-full text-xs font-medium border transition-colors ${
              status === f.value
                ? "bg-teal-500/20 border-teal-500/30 text-teal-300"
                : "bg-slate-800 border-slate-700 text-slate-400 hover:text-white hover:border-slate-600"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-700/30 rounded-xl px-4 py-3">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-28 rounded-xl bg-slate-800/50 animate-pulse" />
          ))}
        </div>
      ) : alerts.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-slate-500">No cluster alerts for the selected status.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* High-priority section */}
          {highPriority.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                <p className="text-xs font-medium text-red-400 uppercase tracking-wider">
                  High Priority ({highPriority.length})
                </p>
              </div>
              {highPriority.map(a => <AlertCard key={a.id} alert={a} />)}
            </div>
          )}

          {/* Standard alerts */}
          {rest.length > 0 && (
            <div className="space-y-3">
              {highPriority.length > 0 && (
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Standard ({rest.length})
                </p>
              )}
              {rest.map(a => <AlertCard key={a.id} alert={a} />)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function AlertCard({ alert: a }: { alert: ClusterAlert }) {
  const isHigh = (a.cluster_score ?? 0) >= 35;
  return (
    <div className={`bg-slate-900 border rounded-xl p-5 space-y-3 ${
      isHigh ? "border-red-700/30" : "border-slate-800"
    }`}>
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-sm font-medium text-white leading-snug">{a.title}</h3>
        <div className="flex items-center gap-2 flex-shrink-0">
          <StatusBadge status={a.status} />
          <ScoreBadge score={a.cluster_score} />
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Stat label="Pathogen" value={a.pathogen || "Unknown"} />
        <Stat label="Cases" value={a.case_count_at_open} />
        <Stat label="First onset" value={a.cluster_start_date ?? "—"} />
        <Stat label="Latest onset" value={a.cluster_end_date ?? "—"} />
      </div>

      <div className="flex items-center justify-between pt-1">
        <p className="text-xs text-slate-500">{a.geographic_scope}</p>
        <div className="flex items-center gap-1.5">
          {a.auto_generated && (
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-500">
              auto-detected
            </span>
          )}
          <span className="text-xs text-slate-600">
            Opened {new Date(a.opened_at).toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <p className="text-xs text-slate-500">{label}</p>
      <p className="text-sm font-medium text-white mt-0.5">{value}</p>
    </div>
  );
}
