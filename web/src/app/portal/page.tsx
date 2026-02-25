'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  CalendarDays,
  AlertTriangle,
  Activity,
  ClipboardList,
  ChevronRight,
  CheckCircle2,
  Clock,
  AlertCircle,
} from 'lucide-react';
import {
  getScheduledInspections,
  getAcknowledgments,
  getInvestigations,
  type ScheduledInspection,
  type RecallAcknowledgment,
  type OutbreakInvestigation,
} from '@/lib/health-dept-api';

function StatCard({
  label,
  value,
  sub,
  icon: Icon,
  color,
}: {
  label: string;
  value: number | string;
  sub?: string;
  icon: React.ElementType;
  color: string;
}) {
  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className={`mt-1 text-3xl font-black ${color}`}>{value}</p>
          {sub && <p className="mt-0.5 text-xs text-gray-400">{sub}</p>}
        </div>
        <div className={`rounded-xl p-2 ${color.replace('text-', 'bg-').replace('-700', '-50').replace('-600', '-50')}`}>
          <Icon className={`h-5 w-5 ${color}`} />
        </div>
      </div>
    </div>
  );
}

export default function PortalDashboard() {
  const [schedules, setSchedules] = useState<ScheduledInspection[]>([]);
  const [acks, setAcks] = useState<RecallAcknowledgment[]>([]);
  const [investigations, setInvestigations] = useState<OutbreakInvestigation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const today = new Date().toISOString().split('T')[0];
        const nextWeek = new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0];

        const [sched, ackData, inv] = await Promise.all([
          getScheduledInspections({ status: 'scheduled', since: today, until: nextWeek }),
          getAcknowledgments({ status: 'pending' }),
          getInvestigations({ status: 'open' }),
        ]);
        setSchedules(sched.results);
        setAcks(Array.isArray(ackData) ? ackData : []);
        setInvestigations(Array.isArray(inv) ? inv : []);
      } catch {
        setError('Could not load dashboard data. Make sure the API is running.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="p-8 animate-pulse space-y-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-24 rounded-2xl bg-gray-100" />
        ))}
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-black text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-amber-100 bg-amber-50 px-4 py-3 text-sm text-amber-700">
          {error}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Inspections this week"
          value={schedules.length}
          sub="scheduled"
          icon={CalendarDays}
          color="text-emerald-600"
        />
        <StatCard
          label="Pending acknowledgments"
          value={acks.length}
          sub="recalls awaiting review"
          icon={AlertTriangle}
          color="text-amber-600"
        />
        <StatCard
          label="Open investigations"
          value={investigations.length}
          sub="outbreak clusters"
          icon={Activity}
          color="text-red-600"
        />
        <StatCard
          label="Upcoming inspections"
          value={schedules.filter((s) => s.status === 'scheduled').length}
          sub="next 7 days"
          icon={ClipboardList}
          color="text-sky-600"
        />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Upcoming inspections */}
        <div className="rounded-2xl border bg-white shadow-sm p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-gray-900 flex items-center gap-2">
              <CalendarDays className="h-4 w-4 text-emerald-500" />
              Scheduled this week
            </h2>
            <Link
              href="/portal/inspections"
              className="text-xs text-emerald-600 hover:underline flex items-center gap-0.5"
            >
              View all <ChevronRight className="h-3 w-3" />
            </Link>
          </div>

          {schedules.length === 0 ? (
            <p className="text-sm text-gray-400 py-4 text-center">No inspections scheduled this week.</p>
          ) : (
            <div className="space-y-2">
              {schedules.slice(0, 5).map((s) => (
                <div key={s.id} className="flex items-start justify-between rounded-xl bg-gray-50 px-3 py-2.5 text-sm">
                  <div>
                    <p className="font-medium text-gray-900 truncate max-w-[180px]">{s.restaurant_name}</p>
                    <p className="text-xs text-gray-500">{s.restaurant_city}, {s.restaurant_state}</p>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-xs font-medium text-gray-700">
                      {new Date(s.scheduled_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </p>
                    <p className="text-xs text-gray-400 capitalize">{s.inspection_type.replace('_', ' ')}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          <Link
            href="/portal/inspections/new"
            className="mt-4 flex w-full items-center justify-center rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-100 transition-colors"
          >
            + Schedule inspection
          </Link>
        </div>

        {/* Pending recall acknowledgments */}
        <div className="rounded-2xl border bg-white shadow-sm p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-gray-900 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-500" />
              Recall acknowledgments
            </h2>
            <Link
              href="/portal/recalls"
              className="text-xs text-amber-600 hover:underline flex items-center gap-0.5"
            >
              View all <ChevronRight className="h-3 w-3" />
            </Link>
          </div>

          {acks.length === 0 ? (
            <div className="py-4 text-center">
              <CheckCircle2 className="h-8 w-8 text-emerald-400 mx-auto mb-2" />
              <p className="text-sm text-gray-500">All recalls acknowledged.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {acks.slice(0, 5).map((ack) => (
                <div key={ack.id} className="flex items-start gap-3 rounded-xl bg-amber-50 border border-amber-100 px-3 py-2.5 text-sm">
                  <AlertCircle className="h-4 w-4 text-amber-500 mt-0.5 shrink-0" />
                  <div className="min-w-0">
                    <p className="font-medium text-gray-900 truncate">{ack.recall_title || `Recall #${ack.recall}`}</p>
                    {ack.recall_classification && (
                      <p className="text-xs text-amber-600">Class {ack.recall_classification}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Open outbreak investigations */}
        <div className="rounded-2xl border bg-white shadow-sm p-5 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-gray-900 flex items-center gap-2">
              <Activity className="h-4 w-4 text-red-500" />
              Open outbreak investigations
            </h2>
            <Link
              href="/portal/clusters"
              className="text-xs text-red-600 hover:underline flex items-center gap-0.5"
            >
              View all <ChevronRight className="h-3 w-3" />
            </Link>
          </div>

          {investigations.length === 0 ? (
            <div className="py-4 text-center">
              <CheckCircle2 className="h-8 w-8 text-emerald-400 mx-auto mb-2" />
              <p className="text-sm text-gray-500">No open outbreak investigations.</p>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 gap-3">
              {investigations.slice(0, 4).map((inv) => (
                <div key={inv.id} className="rounded-xl border border-red-100 bg-red-50 px-4 py-3">
                  <div className="flex items-start gap-2">
                    <span className="mt-1 h-2 w-2 rounded-full bg-red-400 animate-pulse shrink-0" />
                    <div>
                      <p className="font-semibold text-sm text-gray-900">{inv.title}</p>
                      {inv.pathogen && (
                        <p className="text-xs text-red-700 mt-0.5">{inv.pathogen}</p>
                      )}
                      <p className="text-xs text-gray-500 mt-1">
                        {inv.case_count_at_open} cases · {inv.geographic_scope}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
