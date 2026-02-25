import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { prefersReducedMotion } from '@/lib/animations/gsap';

/**
 * React Hook for GSAP Animations
 * Provides automatic cleanup and respects accessibility preferences
 */

interface UseGSAPOptions {
  dependencies?: any[];
  reducedMotionFallback?: boolean;
}

/**
 * Basic GSAP animation hook
 */
export const useGSAP = (
  callback: (context: gsap.Context) => any,
  options: UseGSAPOptions = {}
) => {
  const { dependencies = [], reducedMotionFallback = true } = options;
  const contextRef = useRef<gsap.Context>();

  useEffect(() => {
    // Skip animations if user prefers reduced motion
    if (prefersReducedMotion() && reducedMotionFallback) {
      return;
    }

    // Create GSAP context
    contextRef.current = gsap.context(() => {
      callback(contextRef.current!);
    });

    // Cleanup on unmount
    return () => {
      contextRef.current?.revert();
    };
  }, dependencies);

  return contextRef;
};

/**
 * Hook for entrance animations
 */
export const useEntranceAnimation = (
  enabled: boolean = true,
  delay: number = 0
) => {
  const elementRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!enabled || !elementRef.current || prefersReducedMotion()) {
      return;
    }

    const ctx = gsap.context(() => {
      gsap.fromTo(
        elementRef.current,
        {
          opacity: 0,
          y: 30,
        },
        {
          opacity: 1,
          y: 0,
          duration: 0.6,
          delay,
          ease: 'power2.out',
        }
      );
    }, elementRef);

    return () => ctx.revert();
  }, [enabled, delay]);

  return elementRef;
};

/**
 * Hook for staggered children animations
 */
export const useStaggerAnimation = (
  childSelector: string = '.stagger-item',
  staggerAmount: number = 0.1
) => {
  const containerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!containerRef.current || prefersReducedMotion()) {
      return;
    }

    const ctx = gsap.context(() => {
      gsap.fromTo(
        `${childSelector}`,
        {
          opacity: 0,
          y: 20,
        },
        {
          opacity: 1,
          y: 0,
          stagger: staggerAmount,
          duration: 0.5,
          ease: 'power2.out',
        }
      );
    }, containerRef);

    return () => ctx.revert();
  }, [childSelector, staggerAmount]);

  return containerRef;
};

/**
 * Hook for counter animations
 */
export const useCounterAnimation = (
  target: number,
  options: {
    decimals?: number;
    prefix?: string;
    suffix?: string;
    duration?: number;
    enabled?: boolean;
  } = {}
) => {
  const {
    decimals = 1,
    prefix = '',
    suffix = '',
    duration = 1.5,
    enabled = true,
  } = options;
  const elementRef = useRef<HTMLElement>(null);
  const hasAnimated = useRef(false);

  useEffect(() => {
    if (
      !enabled ||
      !elementRef.current ||
      hasAnimated.current ||
      prefersReducedMotion()
    ) {
      if (elementRef.current && !enabled) {
        elementRef.current.textContent = `${prefix}${target.toFixed(decimals)}${suffix}`;
      }
      return;
    }

    hasAnimated.current = true;
    const obj = { value: 0 };

    const ctx = gsap.context(() => {
      gsap.to(obj, {
        value: target,
        duration,
        ease: 'power2.out',
        onUpdate: () => {
          if (elementRef.current) {
            elementRef.current.textContent = `${prefix}${obj.value.toFixed(decimals)}${suffix}`;
          }
        },
      });
    }, elementRef);

    return () => ctx.revert();
  }, [target, decimals, prefix, suffix, duration, enabled]);

  return elementRef;
};

/**
 * Hook for hover animations
 */
export const useHoverAnimation = (
  animationFn: (isHovering: boolean) => gsap.core.Tween
) => {
  const elementRef = useRef<HTMLElement>(null);
  const ctxRef = useRef<gsap.Context | null>(null);

  const handleMouseEnter = () => {
    if (!elementRef.current || prefersReducedMotion()) return;
    ctxRef.current = gsap.context(() => {
      animationFn(true);
    }, elementRef);
  };

  const handleMouseLeave = () => {
    if (!elementRef.current || prefersReducedMotion()) return;
    ctxRef.current?.revert();
    ctxRef.current = gsap.context(() => {
      animationFn(false);
    }, elementRef);
  };

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    element.addEventListener('mouseenter', handleMouseEnter);
    element.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      element.removeEventListener('mouseenter', handleMouseEnter);
      element.removeEventListener('mouseleave', handleMouseLeave);
      ctxRef.current?.revert();
    };
  }, []);

  return elementRef;
};

/**
 * Hook for pulse animation (alerts, loading states)
 */
export const usePulseAnimation = (
  enabled: boolean = true,
  interval: number = 0.5
) => {
  const elementRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!enabled || !elementRef.current || prefersReducedMotion()) {
      return;
    }

    const ctx = gsap.context(() => {
      gsap.to(elementRef.current, {
        scale: 1.05,
        duration: interval,
        repeat: -1,
        yoyo: true,
        ease: 'power1.inOut',
      });
    }, elementRef);

    return () => ctx.revert();
  }, [enabled, interval]);

  return elementRef;
};
