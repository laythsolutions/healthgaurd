import { cn } from '@/lib/utils';

interface GradeBadgeProps {
  grade: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const gradeConfig: Record<string, { label: string; bg: string; text: string; ring: string }> = {
  A: { label: 'A', bg: 'bg-emerald-50', text: 'text-emerald-700', ring: 'ring-emerald-300' },
  B: { label: 'B', bg: 'bg-yellow-50', text: 'text-yellow-700', ring: 'ring-yellow-300' },
  C: { label: 'C', bg: 'bg-orange-50', text: 'text-orange-700', ring: 'ring-orange-300' },
  P: { label: 'P', bg: 'bg-sky-50', text: 'text-sky-700', ring: 'ring-sky-300' },
  X: { label: 'Closed', bg: 'bg-red-50', text: 'text-red-700', ring: 'ring-red-300' },
};

const sizeConfig = {
  sm: 'w-7 h-7 text-xs font-bold',
  md: 'w-10 h-10 text-sm font-bold',
  lg: 'w-14 h-14 text-xl font-black',
  xl: 'w-20 h-20 text-3xl font-black',
};

export function GradeBadge({ grade, size = 'md', className }: GradeBadgeProps) {
  const config = gradeConfig[grade] ?? { label: '?', bg: 'bg-gray-50', text: 'text-gray-400', ring: 'ring-gray-200' };
  return (
    <div
      className={cn(
        'inline-flex items-center justify-center rounded-full ring-2',
        config.bg, config.text, config.ring,
        sizeConfig[size],
        className,
      )}
      aria-label={`Grade ${config.label}`}
    >
      {config.label}
    </div>
  );
}

export function GradeLabel({ grade }: { grade: string }) {
  const labels: Record<string, string> = {
    A: 'Excellent',
    B: 'Good',
    C: 'Needs Improvement',
    P: 'Pending',
    X: 'Closed',
  };
  return <span>{labels[grade] ?? 'Unknown'}</span>;
}
