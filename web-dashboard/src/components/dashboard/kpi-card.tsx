'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { TrendIndicator } from './trend-indicator';
import { useCounterAnimation, useHoverAnimation } from '@/hooks/use-gsap';
import { cn } from '@/lib/utils';
import { lucideIconType } from 'lucide-react';
import { CheckCircle, AlertTriangle, Activity, Thermometer, TrendingUp, TrendingDown } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  icon?: React.ElementType;
  iconColor?: string;
  trend?: number; // Percentage change
  description?: string;
  status?: 'good' | 'warning' | 'critical' | 'neutral';
  className?: string;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  onClick?: () => void;
}

const statusColors = {
  good: 'text-green-500',
  warning: 'text-yellow-500',
  critical: 'text-red-500',
  neutral: 'text-muted-foreground',
};

const statusBgColors = {
  good: 'bg-green-500/10',
  warning: 'bg-yellow-500/10',
  critical: 'bg-red-500/10',
  neutral: 'bg-muted',
};

export function KPICard({
  title,
  value,
  icon: Icon = Activity,
  iconColor = 'text-primary',
  trend,
  description,
  status = 'neutral',
  className,
  decimals = 1,
  prefix = '',
  suffix = '',
  onClick,
}: KPICardProps) {
  const numericValue = typeof value === 'number' ? value : parseFloat(value) || 0;
  const valueRef = useCounterAnimation(numericValue, {
    decimals,
    prefix,
    suffix,
    duration: title === 'Compliance Score' ? 1.5 : 1,
  });

  const cardRef = useHoverAnimation((isHovering) => {
    const card = cardRef.current;
    if (!card) return null as any;
    
    if (isHovering) {
      return window.gsap.to(card, {
        y: -4,
        boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        duration: 0.3,
        ease: 'power2.out',
      });
    } else {
      return window.gsap.to(card, {
        y: 0,
        boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        duration: 0.3,
        ease: 'power2.out',
      });
    }
  });

  return (
    <Card
      ref={cardRef}
      className={cn(
        'group cursor-pointer transition-all duration-300 hover:shadow-lg',
        onClick && 'active:scale-95',
        statusBgColors[status],
        className
      )}
      onClick={onClick}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="flex flex-col">
          <span className="text-sm font-medium text-muted-foreground">
            {title}
          </span>
          {trend !== undefined && (
            <TrendIndicator value={trend} className="mt-1" />
          )}
        </div>
        <div className={cn('p-2 rounded-full bg-background/80', iconColor)}>
          <Icon className="h-4 w-4" />
        </div>
      </CardHeader>
      <CardContent>
        <div
          ref={valueRef}
          className="text-3xl font-bold tracking-tight tabular-nums"
        >
          {prefix}{numericValue.toFixed(decimals)}{suffix}
        </div>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}
