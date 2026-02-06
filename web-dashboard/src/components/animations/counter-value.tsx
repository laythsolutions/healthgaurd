'use client';

import { useEffect, useRef, ForwardedRef, forwardRef, useState } from 'react';
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
    const [displayValue, setDisplayValue] = useState(0);
    const hasAnimated = useRef(false);

    useEffect(() => {
      if (
        !enableAnimation ||
        hasAnimated.current ||
        prefersReducedMotion() ||
        typeof window === 'undefined'
      ) {
        setDisplayValue(value);
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
            setDisplayValue(obj.value);
          },
        });
      }, spanRef);

      return () => ctx.revert();
    }, [value, duration, enableAnimation]);

    return (
      <span
        ref={spanRef}
        className={cn('tabular-nums', className)}
      >
        {prefix}{displayValue.toFixed(decimals)}{suffix}
      </span>
    );
  }
);

CounterValue.displayName = 'CounterValue';
