'use client';

import { useEffect, useRef, ForwardedRef, forwardRef } from 'react';
import { gsap } from 'gsap';
import { cn } from '@/lib/utils';
import { prefersReducedMotion } from '@/lib/animations/gsap';

interface CounterValueProps {
  value: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  duration?: number;
  className?: string;
  enableAnimation?: boolean;
}

export const CounterValue = forwardRef<HTMLSpanElement, CounterValueProps>(
  (
    {
      value,
      decimals = 0,
      prefix = '',
      suffix = '',
      duration = 1.5,
      className,
      enableAnimation = true,
    },
    ref: ForwardedRef<HTMLSpanElement>
  ) => {
    const internalRef = useRef<HTMLSpanElement>(null);
    const spanRef = (ref as React.RefObject<HTMLSpanElement>) || internalRef;
    const hasAnimated = useRef(false);

    useEffect(() => {
      if (
        !spanRef.current ||
        !enableAnimation ||
        hasAnimated.current ||
        prefersReducedMotion()
      ) {
        if (spanRef.current && !enableAnimation) {
          spanRef.current.textContent = `${prefix}${value.toFixed(decimals)}${suffix}`;
        }
        return;
      }

      hasAnimated.current = true;
      const obj = { value: 0 };

      const ctx = gsap.context(() => {
        gsap.to(obj, {
          value: value,
          duration,
          ease: 'power2.out',
          onUpdate: () => {
            if (spanRef.current) {
              spanRef.current.textContent = `${prefix}${obj.value.toFixed(decimals)}${suffix}`;
            }
          },
        });
      }, spanRef);

      return () => ctx.revert();
    }, [value, decimals, prefix, suffix, duration, enableAnimation, spanRef]);

    return (
      <span
        ref={spanRef}
        className={cn('tabular-nums', className)}
      >
        {prefix}{value.toFixed(decimals)}{suffix}
      </span>
    );
  }
);

CounterValue.displayName = 'CounterValue';
