'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import {
  CalendarDays,
  Plus,
  CheckCircle2,
  Clock,
  XCircle,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Filter,
} from 'lucide-react';
import {
  getScheduledInspections,
  updateScheduledInspection,
  type ScheduledInspection,
} from '@/lib/health-dept-api';

const STATUS_CONFIG: Record<
  string,
  { label: string; icon: React.ElementType; dot: string; text: string; bg: string }
> = {
  scheduled:   { label: 'Scheduled',   icon: Clock,         dot: 'bg-sky-400',     text: 'text-sky-700',     bg: 'bg-sky-50' },
  in_progress: { label: 'In progress', icon: AlertCircle,   dot: 'bg-amber-400',   text: 'text-amber-700',   bg: 'bg-amber-50' },
  completed:   { label: 'Completed',   icon: CheckCircle2,  dot: 'bg-emerald-400', text: 'text-emerald-700', bg: 'bg-emerald-50' },
  cancelled:   { label: 'Cancelled',   icon: XCircle,       dot: 'bg-gray-300',    text: 'text-gray-500',    bg: 'bg-gray-50' },
  missed:      { label: 'Missed',      icon: XCircle,       dot: 'bg-red-400',     text: 'text-red-700',     bg: 'bg-red-50' },
};

const PAGE_SIZE = 20;

export default function InspectionsPage() {
  const [schedules, setSchedules] = useState<ScheduledInspection[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getScheduledInspections({
        status: statusFilter || undefined,
        page_size: PAGE_SIZE,
        offset,
      });
      setSchedules(data.results);
      setTotal(data.total);
    } catch {
      setError('Could not load inspections.');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, offset]);

  useEffect(() => { load(); }, [load]);

  async function markStatus(id: number, newStatus: string) {
    setUpdatingId(id);
    try {
      const updated = await updateScheduledInspection(id, { status: newStatus as ScheduledInspection['status'] });
      setSchedules((prev) => prev.map((s) => (s.id === id ? updated : s)));
    } catch {
      setError('Failed to update status.');
    } finally {
      setUpdatingId(null);
    }
  }

  const hasPrev = offset > 0;
  const hasNext = offset + PAGE_SIZE < total;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6 flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-black text-gray-900 flex items-center gap-2">
            <CalendarDays className="h-6 w-6 text-emerald-500" />
            Inspection Schedule
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {total} record{total !== 1 ? 's' : ''}
          </p>
        </div>
        <Link
          href="/portal/inspections/new"
          className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 transition-colors shadow-sm"
        >
          <Plus className="h-4 w-4" /> Schedule inspection
        </Link>
      </div>

      {/* Filters */}
      <div className="mb-6 flex items-center gap-3 flex-wrap">
        <Filter className="h-4 w-4 text-gray-400" />
        {['', 'scheduled', 'in_progress', 'completed', 'missed', 'cancelled'].map((s) => (
          <button
            key={s}
            onClick={() => { setStatusFilter(s); setOffset(0); }}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              statusFilter === s
                ? 'bg-gray-900 text-white'
                : 'bg-white border text-gray-600 hover:border-gray-400'
            }`}
          >
            {s ? STATUS_CONFIG[s]?.label ?? s : 'All statuses'}
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
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-20 rounded-2xl bg-gray-100" />
          ))}
        </div>
      ) : schedules.length === 0 ? (
        <div className="rounded-2xl border bg-white shadow-sm py-16 text-center">
          <CalendarDays className="h-10 w-10 text-gray-300 mx-auto mb-3" />
          <p className="font-medium text-gray-500">No inspections found.</p>
          <Link
            href="/portal/inspections/new"
            className="mt-4 inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700"
          >
            <Plus className="h-4 w-4" /> Schedule one
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {schedules.map((s) => {
            const sc = STATUS_CONFIG[s.status] ?? STATUS_CONFIG.scheduled;
            const StatusIcon = sc.icon;
            return (
              <div key={s.id} className="rounded-2xl border bg-white shadow-sm px-5 py-4">
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${sc.text}`}>
                        <span className={`h-2 w-2 rounded-full ${sc.dot}`} />
                        {sc.label}
                      </span>
                      <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600 capitalize">
                        {s.inspection_type.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="font-bold text-gray-900">{s.restaurant_name}</p>
                    <p className="text-sm text-gray-500">
                      {s.restaurant_address}, {s.restaurant_city}, {s.restaurant_state}
                    </p>
                    {s.notes && (
                      <p className="text-xs text-gray-400 mt-1 italic">{s.notes}</p>
                    )}
                  </div>

                  <div className="text-right shrink-0">
                    <p className="text-sm font-bold text-gray-900">
                      {new Date(s.scheduled_date).toLocaleDateString('en-US', {
                        weekday: 'short', month: 'short', day: 'numeric',
                      })}
                    </p>
                    {s.scheduled_time && (
                      <p className="text-xs text-gray-500">{s.scheduled_time}</p>
                    )}

                    {/* Quick status actions */}
                    {s.status === 'scheduled' && (
                      <div className="flex gap-1.5 mt-2 justify-end">
                        <button
                          disabled={updatingId === s.id}
                          onClick={() => markStatus(s.id, 'in_progress')}
                          className="rounded-lg bg-amber-50 border border-amber-200 px-2 py-1 text-xs text-amber-700 hover:bg-amber-100 disabled:opacity-50"
                        >
                          Start
                        </button>
                        <button
                          disabled={updatingId === s.id}
                          onClick={() => markStatus(s.id, 'cancelled')}
                          className="rounded-lg bg-gray-50 border px-2 py-1 text-xs text-gray-600 hover:bg-gray-100 disabled:opacity-50"
                        >
                          Cancel
                        </button>
                      </div>
                    )}
                    {s.status === 'in_progress' && (
                      <button
                        disabled={updatingId === s.id}
                        onClick={() => markStatus(s.id, 'completed')}
                        className="mt-2 rounded-lg bg-emerald-50 border border-emerald-200 px-2 py-1 text-xs text-emerald-700 hover:bg-emerald-100 disabled:opacity-50"
                      >
                        Mark complete
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Pagination */}
          <div className="flex items-center justify-between pt-2">
            <p className="text-xs text-gray-400">
              {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} of {total}
            </p>
            <div className="flex gap-2">
              <button
                disabled={!hasPrev}
                onClick={() => setOffset((o) => o - PAGE_SIZE)}
                className="inline-flex items-center gap-1 rounded-lg border px-3 py-1.5 text-sm text-gray-600 hover:border-emerald-200 hover:text-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="h-4 w-4" /> Prev
              </button>
              <button
                disabled={!hasNext}
                onClick={() => setOffset((o) => o + PAGE_SIZE)}
                className="inline-flex items-center gap-1 rounded-lg border px-3 py-1.5 text-sm text-gray-600 hover:border-emerald-200 hover:text-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Next <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
