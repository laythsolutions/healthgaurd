import Link from 'next/link';
import { AlertTriangle, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { GradeBadge } from './grade-badge';
import type { Inspection } from '@/lib/public-api';
import { cn } from '@/lib/utils';

interface InspectionTimelineProps {
  inspections: Inspection[];
}

const typeLabel: Record<string, string> = {
  routine: 'Routine',
  follow_up: 'Follow-up',
  complaint: 'Complaint',
  pre_opening: 'Pre-opening',
  reinspection: 'Re-inspection',
  special: 'Special',
};

export function InspectionTimeline({ inspections }: InspectionTimelineProps) {
  if (inspections.length === 0) {
    return (
      <div className="rounded-xl border border-dashed p-8 text-center text-gray-400 text-sm">
        No inspection records available.
      </div>
    );
  }

  return (
    <ol className="relative space-y-0">
      {inspections.map((insp, idx) => (
        <li key={insp.id} className="flex gap-4">
          {/* Timeline line + dot */}
          <div className="flex flex-col items-center">
            <div className={cn(
              'mt-1 h-3 w-3 rounded-full ring-2 ring-white shadow',
              insp.closed ? 'bg-red-400' :
              insp.grade === 'A' ? 'bg-emerald-400' :
              insp.grade === 'B' ? 'bg-yellow-400' :
              insp.grade === 'C' ? 'bg-orange-400' : 'bg-gray-300',
            )} />
            {idx < inspections.length - 1 && (
              <div className="w-px flex-1 bg-gray-100 my-1" />
            )}
          </div>

          {/* Content */}
          <div className="flex-1 pb-6">
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-900">
                    {typeLabel[insp.inspection_type] ?? insp.inspection_type}
                  </span>
                  {insp.closed && (
                    <span className="inline-flex items-center gap-1 rounded-full bg-red-50 px-2 py-0.5 text-xs font-medium text-red-600">
                      <XCircle className="h-3 w-3" /> Closed
                    </span>
                  )}
                </div>
                <time className="text-xs text-gray-400">
                  {new Date(insp.inspected_at).toLocaleDateString('en-US', {
                    year: 'numeric', month: 'long', day: 'numeric',
                  })}
                </time>
                {insp.source_jurisdiction && (
                  <p className="text-xs text-gray-400 mt-0.5">{insp.source_jurisdiction}</p>
                )}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {insp.score !== null && (
                  <span className="text-sm font-medium text-gray-600">{insp.score}/100</span>
                )}
                <GradeBadge grade={insp.grade} size="sm" />
              </div>
            </div>

            {/* Violations summary */}
            {insp.total_violations > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {insp.critical_violations > 0 && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-red-50 px-2 py-0.5 text-xs text-red-700">
                    <AlertTriangle className="h-3 w-3" />
                    {insp.critical_violations} critical
                  </span>
                )}
                <span className="inline-flex items-center gap-1 rounded-full bg-gray-50 px-2 py-0.5 text-xs text-gray-600">
                  {insp.total_violations} total violations
                </span>
              </div>
            )}

            {insp.total_violations === 0 && insp.grade && (
              <div className="mt-2 inline-flex items-center gap-1 text-xs text-emerald-600">
                <CheckCircle2 className="h-3 w-3" /> No violations recorded
              </div>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}
