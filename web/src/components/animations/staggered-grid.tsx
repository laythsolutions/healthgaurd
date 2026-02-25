'use client';

import { forwardRef, ForwardedRef, useEffect, useRef, ReactNode } from 'react';
import { gsap } from 'gsap';
import { cn } from '@/lib/utils';
import { prefersReducedMotion } from '@/lib/animations/gsap';

interface StaggeredGridProps {
  children: ReactNode;
  className?: string;
  cols?: 1 | 2 | 3 | 4;
  staggerAmount?: number;
  animation?: 'fade' | 'slide' | 'scale';
  direction?: 'up' | 'down' | 'left' | 'right';
  delay?: number;
}

export const StaggeredGrid = forwardRef<HTMLDivElement, StaggeredGridProps>(
  (
    {
      children,
      className,
      cols = 3,
      staggerAmount = 0.1,
      animation = 'fade',
      direction = 'up',
      delay = 0,
    },
    ref: ForwardedRef<HTMLDivElement>
  ) => {
    const internalRef = useRef<HTMLDivElement>(null);
    const gridRef = (ref as React.RefObject<HTMLDivElement>) || internalRef;

    const colsClass = {
      1: 'grid-cols-1',
      2: 'grid-cols-1 md:grid-cols-2',
      3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
      4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
    };

    useEffect(() => {
      if (!gridRef.current || prefersReducedMotion()) return;

      const children = Array.from(gridRef.current.children);
      if (children.length === 0) return;

      const positions = {
        up: { y: 30 },
        down: { y: -30 },
        left: { x: 30 },
        right: { x: -30 },
      };

      const fromState = {
        opacity: 0,
        ...positions[direction],
        ...(animation === 'scale' && { scale: 0.95 }),
      };

      const ctx = gsap.context(() => {
        gsap.fromTo(
          children,
          fromState,
          {
            opacity: 1,
            x: 0,
            y: 0,
            scale: 1,
            duration: 0.5,
            delay,
            stagger: staggerAmount,
            ease: 'power2.out',
          }
        );
      }, gridRef);

      return () => ctx.revert();
    }, [staggerAmount, animation, direction, delay, gridRef]);

    return (
      <div
        ref={gridRef}
        className={cn('grid gap-4', colsClass[cols], className)}
      >
        {children}
      </div>
    );
  }
);

StaggeredGrid.displayName = 'StaggeredGrid';

// Wrapper component to mark items for staggered animation
interface StaggerItemProps {
  children: ReactNode;
  className?: string;
}

export function StaggerItem({ children, className }: StaggerItemProps) {
  return <div className={cn('stagger-item', className)}>{children}</div>;
}
