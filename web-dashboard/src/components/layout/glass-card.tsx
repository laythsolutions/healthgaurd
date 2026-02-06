'use client';

import { forwardRef, useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { cn } from '@/lib/utils';
import { prefersReducedMotion } from '@/lib/animations/gsap';

export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'gradient' | 'border' | 'solid';
  intensity?: 'light' | 'medium' | 'heavy';
  glow?: boolean;
  hover?: boolean;
  children: React.ReactNode;
}

export const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  (
    {
      className,
      variant = 'default',
      intensity = 'medium',
      glow = false,
      hover = true,
      children,
      ...props
    },
    ref
  ) => {
    const internalRef = useRef<HTMLDivElement>(null);
    const cardRef = (ref as React.RefObject<HTMLDivElement>) || internalRef;

    useEffect(() => {
      if (!cardRef.current || !hover || prefersReducedMotion()) return;

      const card = cardRef.current;

      const handleMouseMove = (e: MouseEvent) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateX = (y - centerY) / 20;
        const rotateY = (centerX - x) / 20;

        gsap.to(card, {
          rotateX,
          rotateY,
          scale: 1.02,
          duration: 0.3,
          ease: 'power2.out',
        });
      };

      const handleMouseLeave = () => {
        gsap.to(card, {
          rotateX: 0,
          rotateY: 0,
          scale: 1,
          duration: 0.3,
          ease: 'power2.out',
        });
      };

      card.addEventListener('mousemove', handleMouseMove);
      card.addEventListener('mouseleave', handleMouseLeave);

      return () => {
        card.removeEventListener('mousemove', handleMouseMove);
        card.removeEventListener('mouseleave', handleMouseLeave);
      };
    }, [hover, cardRef]);

    const variantStyles = {
      default: 'glass-card',
      gradient: 'bg-gradient-to-br from-violet-500/10 via-indigo-500/10 to-blue-500/10 backdrop-blur-xl border border-white/20',
      border: 'bg-background/80 backdrop-blur-xl border-2 border-transparent bg-clip-padding',
      solid: 'bg-card border border-border',
    };

    const intensityStyles = {
      light: 'shadow-lg',
      medium: 'shadow-xl',
      heavy: 'shadow-2xl',
    };

    return (
      <div
        ref={cardRef}
        className={cn(
          'rounded-xl transition-all duration-300',
          variantStyles[variant],
          intensityStyles[intensity],
          glow && 'hover:glow-violet',
          hover && 'cursor-pointer',
          className
        )}
        style={{ transformStyle: 'preserve-3d', perspective: '1000px' }}
        {...props}
      >
        {children}
      </div>
    );
  }
);

GlassCard.displayName = 'GlassCard';
