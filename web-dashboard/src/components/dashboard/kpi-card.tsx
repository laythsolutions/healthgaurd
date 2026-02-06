'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { TrendIndicator } from './trend-indicator';
import { useCounterAnimation, useHoverAnimation } from '@/hooks/use-gsap';
import { GlassCard } from '@/components/layout/glass-card';
import { CounterValue, GradientText, FloatingElement } from '@/components/animations';
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
  variant?: 'default' | 'gradient' | 'glass';
  gradient?: string;
}

const statusColors = {
  good: 'text-emerald-500',
  warning: 'text-amber-500',
  critical: 'text-rose-500',
  neutral: 'text-muted-foreground',
};

const statusGradients = {
  good: 'from-emerald-500/10 to-green-500/10',
  warning: 'from-amber-500/10 to-orange-500/10',
  critical: 'from-rose-500/10 to-red-500/10',
  neutral: 'from-muted to-muted',
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
  variant = 'default',
  gradient,
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
        y: -8,
        scale: 1.02,
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0 / 0.15), 0 0 0 1px rgba(139, 92, 246, 0.2)',
        duration: 0.3,
        ease: 'power2.out',
      });
    } else {
      return window.gsap.to(card, {
        y: 0,
        scale: 1,
        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        duration: 0.3,
        ease: 'power2.out',
      });
    }
  });

  const bgGradient = gradient || statusGradients[status];

  if (variant === 'glass') {
    return (
      <GlassCard
        ref={cardRef}
        className={cn(
          'group cursor-pointer',
          onClick && 'active:scale-95',
          className
        )}
        onClick={onClick}
        variant="gradient"
        glow={status === 'critical'}
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
          <FloatingElement intensity="subtle" duration={4}>
            <div className={cn('p-3 rounded-full bg-gradient-to-br', bgGradient, statusColors[status])}>
              <Icon className="h-5 w-5" />
            </div>
          </FloatingElement>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold tracking-tight tabular-nums">
            <CounterValue
              value={numericValue}
              decimals={decimals}
              prefix={prefix}
              suffix={suffix}
            />
          </div>
          {description && (
            <p className="text-xs text-muted-foreground mt-1">{description}</p>
          )}
        </CardContent>
      </GlassCard>
    );
  }

  return (
    <Card
      ref={cardRef}
      className={cn(
        'group cursor-pointer transition-all duration-300 hover:shadow-xl card-lift',
        onClick && 'active:scale-95',
        'bg-gradient-to-br',
        bgGradient,
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
        <FloatingElement intensity="subtle" duration={4}>
          <div className={cn('p-3 rounded-full bg-background/80 backdrop-blur', statusColors[status])}>
            <Icon className="h-5 w-5" />
          </div>
        </FloatingElement>
      </CardHeader>
      <CardContent>
        {variant === 'gradient' ? (
          <GradientText
            variant={status === 'good' ? 'success' : status === 'warning' ? 'warning' : status === 'critical' ? 'critical' : 'primary'}
            className="text-3xl"
          >
            <CounterValue
              value={numericValue}
              decimals={decimals}
              prefix={prefix}
              suffix={suffix}
            />
          </GradientText>
        ) : (
          <div className="text-3xl font-bold tracking-tight tabular-nums">
            <CounterValue
              value={numericValue}
              decimals={decimals}
              prefix={prefix}
              suffix={suffix}
            />
          </div>
        )}
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}
