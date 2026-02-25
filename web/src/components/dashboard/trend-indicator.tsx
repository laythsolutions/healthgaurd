import { ArrowUp, ArrowDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TrendIndicatorProps {
  value: number; // Percentage change
  className?: string;
  showIcon?: boolean;
}

export function TrendIndicator({
  value,
  className,
  showIcon = true,
}: TrendIndicatorProps) {
  const isPositive = value > 0;
  const isNeutral = value === 0;
  const isNegative = value < 0;

  // For compliance, higher is better (green)
  // For alerts, lower is better (green)
  const colorClass = isPositive
    ? 'text-green-500'
    : isNegative
    ? 'text-red-500'
    : 'text-muted-foreground';

  const Icon = isPositive ? ArrowUp : isNegative ? ArrowDown : Minus;

  return (
    <div className={cn('flex items-center gap-1 text-xs font-medium', colorClass, className)}>
      {showIcon && <Icon className="h-3 w-3" />}
      <span>{Math.abs(value).toFixed(1)}%</span>
    </div>
  );
}
