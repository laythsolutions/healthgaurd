'use client';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

type TimeRange = '24h' | '7d' | '30d' | '90d';

interface TimeRangeSelectorProps {
  value: TimeRange;
  onChange: (range: TimeRange) => void;
  className?: string;
}

const ranges: { value: TimeRange; label: string }[] = [
  { value: '24h', label: '24 Hours' },
  { value: '7d', label: '7 Days' },
  { value: '30d', label: '30 Days' },
  { value: '90d', label: '90 Days' },
];

export function TimeRangeSelector({
  value,
  onChange,
  className,
}: TimeRangeSelectorProps) {
  return (
    <div className={cn('inline-flex rounded-lg bg-muted p-1', className)}>
      {ranges.map((range) => (
        <Button
          key={range.value}
          variant={value === range.value ? 'default' : 'ghost'}
          size="sm"
          onClick={() => onChange(range.value)}
          className="h-7 min-w-[60px] text-xs"
        >
          {range.label}
        </Button>
      ))}
    </div>
  );
}
