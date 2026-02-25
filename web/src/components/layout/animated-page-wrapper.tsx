'use client';

import { useEffect, useRef, ReactNode, forwardRef } from 'react';
import { gsap } from 'gsap';
import { cn } from '@/lib/utils';
import { prefersReducedMotion } from '@/lib/animations/gsap';

interface AnimatedPageWrapperProps {
  children: ReactNode;
  className?: string;
  animation?: 'fade' | 'slide' | 'scale' | 'stagger';
  delay?: number;
  staggerAmount?: number;
  childSelector?: string;
}

export const AnimatedPageWrapper = forwardRef<HTMLDivElement, AnimatedPageWrapperProps>(
  (
    {
      children,
      className,
      animation = 'fade',
      delay = 0,
      staggerAmount = 0.1,
      childSelector,
    },
    ref
  ) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const internalRef = (ref as React.RefObject<HTMLDivElement>) || containerRef;

    useEffect(() => {
      if (!internalRef.current || prefersReducedMotion()) return;

      const ctx = gsap.context(() => {
        const targets = childSelector
          ? `${childSelector}`
          : internalRef.current?.children;

        switch (animation) {
          case 'fade':
            gsap.fromTo(
              targets,
              { opacity: 0, y: 30 },
              {
                opacity: 1,
                y: 0,
                duration: 0.6,
                delay,
                stagger: childSelector ? staggerAmount : 0,
                ease: 'power2.out',
              }
            );
            break;

          case 'slide':
            gsap.fromTo(
              targets,
              { opacity: 0, x: -50 },
              {
                opacity: 1,
                x: 0,
                duration: 0.6,
                delay,
                stagger: childSelector ? staggerAmount : 0,
                ease: 'power2.out',
              }
            );
            break;

          case 'scale':
            gsap.fromTo(
              targets,
              { opacity: 0, scale: 0.9 },
              {
                opacity: 1,
                scale: 1,
                duration: 0.5,
                delay,
                stagger: childSelector ? staggerAmount : 0,
                ease: 'back.out(1.7)',
              }
            );
            break;

          case 'stagger':
            gsap.fromTo(
              targets,
              { opacity: 0, y: 20, scale: 0.95 },
              {
                opacity: 1,
                y: 0,
                scale: 1,
                duration: 0.5,
                delay,
                stagger: staggerAmount,
                ease: 'power2.out',
              }
            );
            break;
        }
      }, internalRef);

      return () => ctx.revert();
    }, [animation, delay, staggerAmount, childSelector, internalRef]);

    return (
      <div ref={internalRef} className={className}>
        {children}
      </div>
    );
  }
);

AnimatedPageWrapper.displayName = 'AnimatedPageWrapper';

// Wrapper for staggered grid layouts
interface StaggeredGridProps {
  children: ReactNode;
  className?: string;
  cols?: 1 | 2 | 3 | 4;
  staggerAmount?: number;
}

export function StaggeredGrid({
  children,
  className,
  cols = 3,
  staggerAmount = 0.1,
}: StaggeredGridProps) {
  const colsClass = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  };

  return (
    <AnimatedPageWrapper
      animation="stagger"
      staggerAmount={staggerAmount}
      childSelector=".stagger-item"
      className={cn('grid gap-4', colsClass[cols], className)}
    >
      {children}
    </AnimatedPageWrapper>
  );
}
