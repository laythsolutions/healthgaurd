'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ChevronLeft, CalendarDays, CheckCircle2 } from 'lucide-react';
import { createScheduledInspection } from '@/lib/health-dept-api';

const INSPECTION_TYPES = [
  { value: 'routine',      label: 'Routine' },
  { value: 'follow_up',    label: 'Follow-up' },
  { value: 'complaint',    label: 'Complaint-driven' },
  { value: 'pre_opening',  label: 'Pre-opening' },
  { value: 'reinspection', label: 'Re-inspection' },
  { value: 'special',      label: 'Special' },
];

export default function NewInspectionPage() {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState({
    restaurant: '',
    scheduled_date: '',
    scheduled_time: '',
    inspection_type: 'routine',
    assigned_inspector_id: '',
    jurisdiction: '',
    notes: '',
  });

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.restaurant || !form.scheduled_date) {
      setError('Restaurant ID and scheduled date are required.');
      return;
    }

    setSaving(true);
    setError('');
    try {
      await createScheduledInspection({
        restaurant: parseInt(form.restaurant, 10),
        scheduled_date: form.scheduled_date,
        scheduled_time: form.scheduled_time || undefined,
        inspection_type: form.inspection_type as never,
        assigned_inspector_id: form.assigned_inspector_id,
        jurisdiction: form.jurisdiction,
        notes: form.notes,
      });
      setSaved(true);
      setTimeout(() => router.push('/portal/inspections'), 1500);
    } catch {
      setError('Failed to schedule inspection. Check that the restaurant ID is valid.');
    } finally {
      setSaving(false);
    }
  }

  if (saved) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4 p-8">
        <CheckCircle2 className="h-14 w-14 text-emerald-500" />
        <p className="text-xl font-bold text-gray-900">Inspection scheduled!</p>
        <p className="text-sm text-gray-500">Redirecting to the schedule…</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <Link
        href="/portal/inspections"
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-emerald-700 transition-colors mb-6"
      >
        <ChevronLeft className="h-4 w-4" /> Back to schedule
      </Link>

      <h1 className="text-2xl font-black text-gray-900 mb-1 flex items-center gap-2">
        <CalendarDays className="h-6 w-6 text-emerald-500" />
        Schedule an inspection
      </h1>
      <p className="text-sm text-gray-500 mb-8">Create a planned inspection and assign it to an inspector.</p>

      {error && (
        <div className="mb-6 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="rounded-2xl border bg-white shadow-sm p-6 space-y-5">
          <h2 className="font-bold text-gray-900">Establishment</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Restaurant ID <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              name="restaurant"
              value={form.restaurant}
              onChange={handleChange}
              placeholder="e.g. 42"
              required
              className="w-full rounded-xl border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300"
            />
            <p className="mt-1 text-xs text-gray-400">
              Use the restaurant ID from the database. Future versions will include a search widget.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Jurisdiction</label>
            <input
              type="text"
              name="jurisdiction"
              value={form.jurisdiction}
              onChange={handleChange}
              placeholder="e.g. LA County, NYC DOHMH"
              className="w-full rounded-xl border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300"
            />
          </div>
        </div>

        <div className="rounded-2xl border bg-white shadow-sm p-6 space-y-5">
          <h2 className="font-bold text-gray-900">Inspection details</h2>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                name="scheduled_date"
                value={form.scheduled_date}
                onChange={handleChange}
                required
                className="w-full rounded-xl border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Time (optional)</label>
              <input
                type="time"
                name="scheduled_time"
                value={form.scheduled_time}
                onChange={handleChange}
                className="w-full rounded-xl border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Inspection type</label>
            <select
              name="inspection_type"
              value={form.inspection_type}
              onChange={handleChange}
              className="w-full rounded-xl border px-3 py-2.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-300"
            >
              {INSPECTION_TYPES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Assigned inspector ID</label>
            <input
              type="text"
              name="assigned_inspector_id"
              value={form.assigned_inspector_id}
              onChange={handleChange}
              placeholder="Inspector badge / employee ID"
              className="w-full rounded-xl border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              name="notes"
              value={form.notes}
              onChange={handleChange}
              rows={3}
              placeholder="Any pre-inspection notes or instructions…"
              className="w-full rounded-xl border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 resize-none"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full rounded-xl bg-emerald-600 py-3 text-sm font-semibold text-white hover:bg-emerald-700 transition-colors disabled:opacity-60 shadow-sm"
        >
          {saving ? 'Scheduling…' : 'Schedule inspection'}
        </button>
      </form>
    </div>
  );
}
