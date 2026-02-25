import Link from 'next/link';
import { AlertTriangle, Package, MapPin, Building2 } from 'lucide-react';
import type { Recall } from '@/lib/public-api';
import { cn } from '@/lib/utils';

interface RecallCardProps {
  recall: Recall;
}

const classConfig: Record<string, { label: string; bg: string; text: string }> = {
  I:   { label: 'Class I',   bg: 'bg-red-50',    text: 'text-red-700' },
  II:  { label: 'Class II',  bg: 'bg-orange-50', text: 'text-orange-700' },
  III: { label: 'Class III', bg: 'bg-yellow-50', text: 'text-yellow-700' },
  '':  { label: 'Unclassified', bg: 'bg-gray-50', text: 'text-gray-500' },
};

const sourceLabel: Record<string, string> = {
  fda: 'FDA',
  usda_fsis: 'USDA FSIS',
  cdc: 'CDC',
  manual: 'Manual',
};

const hazardColors: Record<string, string> = {
  Salmonella: 'bg-red-100 text-red-700',
  Listeria: 'bg-red-100 text-red-700',
  'E. coli': 'bg-red-100 text-red-700',
  'Undeclared allergen': 'bg-amber-100 text-amber-700',
  'Foreign material': 'bg-gray-100 text-gray-700',
  Mislabeling: 'bg-gray-100 text-gray-700',
  Contamination: 'bg-orange-100 text-orange-700',
};

export function RecallCard({ recall }: RecallCardProps) {
  const cls = classConfig[recall.classification] ?? classConfig[''];

  return (
    <Link
      href={`/recalls/${recall.id}`}
      className="group block rounded-2xl border bg-white p-5 shadow-sm transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 hover:border-red-100"
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <span className={cn('rounded-full px-2 py-0.5 text-xs font-semibold', cls.bg, cls.text)}>
              {cls.label}
            </span>
            <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
              {sourceLabel[recall.source] ?? recall.source}
            </span>
            {recall.hazard_type && (
              <span className={cn(
                'rounded-full px-2 py-0.5 text-xs font-medium',
                hazardColors[recall.hazard_type] ?? 'bg-gray-100 text-gray-600',
              )}>
                {recall.hazard_type}
              </span>
            )}
          </div>

          <h3 className="font-semibold text-gray-900 group-hover:text-red-700 transition-colors line-clamp-2 text-sm leading-snug">
            {recall.title}
          </h3>
        </div>

        <AlertTriangle className={cn(
          'h-5 w-5 shrink-0 mt-0.5',
          recall.classification === 'I' ? 'text-red-500' :
          recall.classification === 'II' ? 'text-orange-400' : 'text-yellow-400',
        )} />
      </div>

      {/* Details */}
      <div className="mt-3 flex flex-wrap gap-3 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <Building2 className="h-3 w-3" />
          {recall.recalling_firm}
        </span>
        {recall.affected_states.length > 0 && (
          <span className="flex items-center gap-1">
            <MapPin className="h-3 w-3" />
            {recall.affected_states.length > 5
              ? `${recall.affected_states.slice(0, 5).join(', ')} +${recall.affected_states.length - 5} more`
              : recall.affected_states.join(', ')}
          </span>
        )}
        {recall.product_count !== undefined && (
          <span className="flex items-center gap-1">
            <Package className="h-3 w-3" />
            {recall.product_count} product{recall.product_count !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {recall.recall_initiation_date && (
        <time className="mt-2 block text-xs text-gray-400">
          Initiated: {new Date(recall.recall_initiation_date).toLocaleDateString()}
        </time>
      )}
    </Link>
  );
}

export function RecallCardSkeleton() {
  return (
    <div className="animate-pulse rounded-2xl border bg-white p-5 shadow-sm space-y-3">
      <div className="flex gap-2">
        <div className="h-4 w-16 rounded-full bg-gray-100" />
        <div className="h-4 w-12 rounded-full bg-gray-100" />
      </div>
      <div className="h-4 w-full rounded bg-gray-100" />
      <div className="h-3 w-2/3 rounded bg-gray-100" />
    </div>
  );
}
