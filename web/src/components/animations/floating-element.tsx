'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { cn } from '@/lib/utils';
import { prefersReducedMotion } from '@/lib/animations/gsap';

interface FloatingElementProps {
  children: React.ReactNode;
  className?: string;
  intensity?: 'subtle' | 'medium' | 'strong';
  duration?: number;
  enableRotate?: boolean;
  followMouse?: boolean;
}

export function FloatingElement({
  children,
  className,
  intensity = 'subtle',
  duration = 3,
  enableRotate = false,
  followMouse = false,
}: FloatingElementProps) {
  const elementRef = useRef<HTMLDivElement>(null);

  const intensityValues = {
    subtle: { y: 10, rotate: 5 },
    medium: { y: 20, rotate: 10 },
    strong: { y: 30, rotate: 15 },
  };

  useEffect(() => {
    if (!elementRef.current || prefersReducedMotion()) return;

    const { y, rotate } = intensityValues[intensity];
    const ctx = gsap.context(() => {
      // Floating animation
      gsap.to(elementRef.current, {
        y: -y,
        duration,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
      });

      // Optional rotation
      if (enableRotate) {
        gsap.to(elementRef.current, {
          rotation: rotate,
          duration: duration * 2,
          repeat: -1,
          yoyo: true,
          ease: 'sine.inOut',
        });
      }
    }, elementRef);

    return () => ctx.revert();
  }, [intensity, duration, enableRotate]);

  // Mouse follow effect
  useEffect(() => {
    if (!followMouse || !elementRef.current || prefersReducedMotion()) return;

    const element = elementRef.current;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = element.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      const moveX = (e.clientX - centerX) / 20;
      const moveY = (e.clientY - centerY) / 20;

      gsap.to(element, {
        x: moveX,
        y: moveY,
        duration: 0.5,
        ease: 'power2.out',
      });
    };

    const handleMouseLeave = () => {
      gsap.to(element, {
        x: 0,
        y: 0,
        duration: 0.5,
        ease: 'power2.out',
      });
    };

    document.addEventListener('mousemove', handleMouseMove);
    element.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      element.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [followMouse]);

  return (
    <div ref={elementRef} className={cn('inline-block', className)}>
      {children}
    </div>
  );
}
