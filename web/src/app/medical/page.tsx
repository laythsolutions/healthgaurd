"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  getRecentCases,
  getClusterAlerts,
  type SubmittedCase,
  type ClusterAlert,
} from "@/lib/medical-api";

function StatCard({
  label,
  value,
  sub,
  color = "teal",
}: {
  label: string;
  value: number | string;
  sub?: string;
  color?: string;
}) {
  const colors: Record<string, string> = {
    teal:   "bg-teal-500/10 border-teal-500/20 text-teal-400",
    amber:  "bg-amber-500/10 border-amber-500/20 text-amber-400",
    red:    "bg-red-500/10   border-red-500/20   text-red-400",
    blue:   "bg-blue-500/10  border-blue-500/20  text-blue-400",
  };
  return (
    <div className={`rounded-xl border p-5 ${colors[color]}`}>
      <p className="text-xs font-medium uppercase tracking-wider opacity-70">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      {sub && <p className="text-xs opacity-60 mt-0.5">{sub}</p>}
    </div>
  );
}

export default function MedicalDashboard() {
  const [cases, setCases] = useState<SubmittedCase[]>([]);
  const [alerts, setAlerts] = useState<ClusterAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      getRecentCases(10),
      getClusterAlerts("open"),
    ])
      .then(([casesData, alertsData]) => {
        setCases(casesData.results);
        setAlerts(alertsData);
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const thisWeek = cases.filter(c => {
    if (!c.created_at) return false;
    const d = new Date(c.created_at);
    const now = new Date();
    return now.getTime() - d.getTime() < 7 * 24 * 60 * 60 * 1000;
  }).length;

  const confirmed = cases.filter(c => c.illness_status === "confirmed").length;
  const highPriority = alerts.filter(a => (a.cluster_score ?? 0) >= 35).length;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Anonymized case submissions and cluster alerts
          </p>
        </div>
        <Link
          href="/medical/submit"
          className="flex items-center gap-2 bg-teal-500 hover:bg-teal-400 text-black text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          Submit Case
        </Link>
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-700/30 rounded-xl px-4 py-3">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {/* Stats */}
      {loading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-24 rounded-xl bg-slate-800/50 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Submitted (recent)" value={cases.length} sub="shown below" color="teal" />
          <StatCard label="This week" value={thisWeek} color="blue" />
          <StatCard label="Confirmed cases" value={confirmed} color="amber" />
          <StatCard label="Open cluster alerts" value={alerts.length} sub={highPriority > 0 ? `${highPriority} high priority` : undefined} color={alerts.length > 0 ? "red" : "teal"} />
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent submissions */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white">Recent Submissions</h2>
            <span className="text-xs text-slate-500">Your institution only</span>
          </div>

          {loading ? (
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-12 rounded-lg bg-slate-800/50 animate-pulse" />
              ))}
            </div>
          ) : cases.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-slate-500 text-sm">No cases submitted yet.</p>
              <Link href="/medical/submit" className="text-teal-400 text-sm hover:underline mt-1 inline-block">
                Submit your first case
              </Link>
            </div>
          ) : (
            <ul className="space-y-2">
              {cases.map(c => (
                <li key={c.id} className="flex items-center justify-between py-2 border-b border-slate-800 last:border-0">
                  <div>
                    <p className="text-sm text-white">
                      {c.pathogen || "Pathogen unknown"} · {c.age_range || "age N/A"}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Onset {c.onset_date} · {c.zip3 ? `ZIP ${c.zip3}xx` : c.geohash}
                    </p>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full border ${
                    c.illness_status === "confirmed"
                      ? "bg-green-900/30 border-green-700/30 text-green-400"
                      : c.illness_status === "ruled_out"
                      ? "bg-slate-800 border-slate-700 text-slate-500"
                      : "bg-amber-900/20 border-amber-700/20 text-amber-400"
                  }`}>
                    {c.illness_status}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Cluster alerts */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white">Open Cluster Alerts</h2>
            <Link href="/medical/clusters" className="text-xs text-teal-400 hover:underline">
              View all
            </Link>
          </div>

          {loading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-16 rounded-lg bg-slate-800/50 animate-pulse" />
              ))}
            </div>
          ) : alerts.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-slate-500 text-sm">No open cluster alerts.</p>
            </div>
          ) : (
            <ul className="space-y-2">
              {alerts.slice(0, 5).map(a => (
                <li key={a.id} className="p-3 rounded-lg bg-slate-800/50 border border-slate-700/50">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm text-white leading-snug">{a.title}</p>
                    {(a.cluster_score ?? 0) >= 35 && (
                      <span className="flex-shrink-0 text-xs px-1.5 py-0.5 rounded bg-red-900/40 border border-red-700/30 text-red-400">
                        HIGH
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    {a.case_count_at_open} cases · {a.geographic_scope}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
