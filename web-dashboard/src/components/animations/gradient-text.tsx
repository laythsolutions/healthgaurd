'use client';

import { forwardRef, ForwardedRef } from 'react';
import { cn } from '@/lib/utils';

interface GradientTextProps {
  children: React.ReactNode;
  variant?: 'primary' | 'cyan' | 'success' | 'warning' | 'critical' | 'custom';
  className?: string;
  from?: string;
  via?: string;
  to?: string;
  animate?: boolean;
}

export const GradientText = forwardRef<HTMLSpanElement, GradientTextProps>(
  (
    {
      children,
      variant = 'primary',
      className,
      from,
      via,
      to,
      animate = false,
    },
    ref: ForwardedRef<HTMLSpanElement>
  ) => {
    const variants = {
      primary: 'from-violet-600 via-indigo-600 to-blue-600',
      cyan: 'from-cyan-500 via-blue-500 to-indigo-500',
      success: 'from-emerald-500 via-green-500 to-teal-500',
      warning: 'from-amber-500 via-orange-500 to-yellow-500',
      critical: 'from-rose-500 via-red-500 to-pink-500',
      custom: '',
    };

    const gradientClass = variant === 'custom' ? '' : variants[variant];
    const customStyle = variant === 'custom' ? {
      backgroundImage: from && via && to
        ? `linear-gradient(135deg, ${from}, ${via}, ${to})`
        : undefined,
    } : {};

    return (
      <span
        ref={ref}
        className={cn(
          'bg-gradient-to-r bg-clip-text text-transparent font-bold',
          gradientClass,
          animate && 'animate-gradient-shift bg-[length:200%_auto]',
          className
        )}
        style={customStyle}
      >
        {children}
      </span>
    );
  }
);

GradientText.displayName = 'GradientText';
