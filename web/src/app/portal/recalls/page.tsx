'use client';

import { useEffect, useState, useCallback } from 'react';
import { AlertTriangle, CheckCircle2, AlertCircle, Package } from 'lucide-react';
import {
  getAcknowledgments,
  updateAcknowledgment,
  type RecallAcknowledgment,
} from '@/lib/health-dept-api';

const STATUS_OPTIONS = [
  { value: 'pending',       label: 'Pending review',       color: 'bg-amber-50 text-amber-700 border-amber-200' },
  { value: 'acknowledged',  label: 'Acknowledged',         color: 'bg-sky-50 text-sky-700 border-sky-200' },
  { value: 'not_affected',  label: 'Not affected',         color: 'bg-gray-50 text-gray-600 border-gray-200' },
  { value: 'remediated',    label: 'Product removed',      color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  { value: 'escalated',     label: 'Escalated',            color: 'bg-red-50 text-red-700 border-red-200' },
];

function statusStyle(s: string) {
  return STATUS_OPTIONS.find((o) => o.value === s)?.color ?? '';
}

export default function RecallManagementPage() {
  const [acks, setAcks] = useState<RecallAcknowledgment[]>([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatingId, setUpdatingId] = useState<number | null>(null);
  const [notesEdit, setNotesEdit] = useState<Record<number, string>>({});

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getAcknowledgments({ status: filter || undefined });
      setAcks(Array.isArray(data) ? data : []);
    } catch {
      setError('Could not load recall acknowledgments.');
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  async function updateStatus(id: number, newStatus: string) {
    setUpdatingId(id);
    try {
      const updated = await updateAcknowledgment(id, {
        status: newStatus as RecallAcknowledgment['status'],
        notes: notesEdit[id] ?? undefined,
      });
      setAcks((prev) => prev.map((a) => (a.id === id ? updated : a)));
    } catch {
      setError('Failed to update recall status.');
    } finally {
      setUpdatingId(null);
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-black text-gray-900 flex items-center gap-2">
          <AlertTriangle className="h-6 w-6 text-amber-500" />
          Recall Management
        </h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Track recall acknowledgment and remediation status for your establishments.
        </p>
      </div>

      {/* Status filter */}
      <div className="mb-6 flex gap-2 flex-wrap">
        {[{ value: '', label: 'All' }, ...STATUS_OPTIONS].map(({ value, label }) => (
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
          {[...Array(4)].map((_, i) => <div key={i} className="h-28 rounded-2xl bg-gray-100" />)}
        </div>
      ) : acks.length === 0 ? (
        <div className="rounded-2xl border bg-white shadow-sm py-16 text-center">
          <CheckCircle2 className="h-10 w-10 text-emerald-400 mx-auto mb-3" />
          <p className="font-medium text-gray-500">No recall acknowledgments found.</p>
          {filter && (
            <button
              onClick={() => setFilter('')}
              className="mt-3 text-sm text-emerald-600 hover:underline"
            >
              Clear filter
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {acks.map((ack) => (
            <div key={ack.id} className="rounded-2xl border bg-white shadow-sm p-5">
              <div className="flex items-start justify-between gap-4 flex-wrap mb-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${statusStyle(ack.status)}`}>
                      {STATUS_OPTIONS.find((o) => o.value === ack.status)?.label ?? ack.status}
                    </span>
                    {ack.recall_classification && (
                      <span className="rounded-full bg-red-50 border border-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">
                        Class {ack.recall_classification}
                      </span>
                    )}
                    {ack.recall_hazard_type && (
                      <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                        {ack.recall_hazard_type}
                      </span>
                    )}
                  </div>
                  <p className="font-bold text-gray-900 text-sm">
                    {ack.recall_title || `Recall #${ack.recall}`}
                  </p>
                </div>
                <div className="text-right text-xs text-gray-400 shrink-0">
                  <p>Updated {new Date(ack.updated_at).toLocaleDateString()}</p>
                  {ack.units_removed != null && (
                    <p className="mt-0.5 font-medium text-gray-600">{ack.units_removed} units removed</p>
                  )}
                </div>
              </div>

              {/* Notes */}
              <div className="mb-4">
                <textarea
                  placeholder="Add notes…"
                  rows={2}
                  value={notesEdit[ack.id] ?? ack.notes}
                  onChange={(e) => setNotesEdit((prev) => ({ ...prev, [ack.id]: e.target.value }))}
                  className="w-full rounded-xl border bg-gray-50 px-3 py-2 text-xs text-gray-700 focus:outline-none focus:ring-2 focus:ring-amber-200 resize-none"
                />
              </div>

              {/* Action buttons */}
              <div className="flex flex-wrap gap-2">
                {STATUS_OPTIONS.filter((o) => o.value !== ack.status).map((opt) => (
                  <button
                    key={opt.value}
                    disabled={updatingId === ack.id}
                    onClick={() => updateStatus(ack.id, opt.value)}
                    className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors disabled:opacity-50 ${opt.color}`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
