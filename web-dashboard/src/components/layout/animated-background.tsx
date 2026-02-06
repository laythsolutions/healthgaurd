'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { cn } from '@/lib/utils';

interface AnimatedBackgroundProps {
  className?: string;
  variant?: 'gradient' | 'mesh' | 'particles';
  intensity?: 'low' | 'medium' | 'high';
}

export function AnimatedBackground({
  className,
  variant = 'gradient',
  intensity = 'medium',
}: AnimatedBackgroundProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const blobRefs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    if (!containerRef.current) return;

    const ctx = gsap.context(() => {
      // Animate gradient blobs
      blobRefs.current.forEach((blob, index) => {
        if (!blob) return;

        const duration = intensity === 'high' ? 8 : intensity === 'medium' ? 12 : 20;
        const yOffset = 30 + index * 20;

        gsap.to(blob, {
          y: `-=${yOffset}`,
          x: `+=${20 + index * 10}`,
          scale: 1.1 + index * 0.05,
          rotation: index % 2 === 0 ? 90 : -90,
          duration,
          repeat: -1,
          yoyo: true,
          ease: 'sine.inOut',
          delay: index * 0.5,
        });
      });
    }, containerRef);

    return () => ctx.revert();
  }, [intensity]);

  const blobs = [
    {
      className: 'absolute w-96 h-96 bg-violet-500/30 rounded-full blur-3xl',
      style: { top: '10%', left: '10%' },
    },
    {
      className: 'absolute w-80 h-80 bg-indigo-500/30 rounded-full blur-3xl',
      style: { top: '60%', right: '10%' },
    },
    {
      className: 'absolute w-72 h-72 bg-cyan-500/30 rounded-full blur-3xl',
      style: { bottom: '10%', left: '30%' },
    },
    {
      className: 'absolute w-64 h-64 bg-blue-500/20 rounded-full blur-3xl',
      style: { top: '30%', right: '30%' },
    },
  ];

  return (
    <div
      ref={containerRef}
      className={cn(
        'fixed inset-0 -z-10 overflow-hidden',
        variant === 'gradient' && 'animated-gradient-slow',
        className
      )}
    >
      {/* Animated gradient blobs */}
      <div className="absolute inset-0">
        {blobs.map((blob, index) => (
          <div
            key={index}
            ref={(el) => (blobRefs.current[index] = el)}
            className={blob.className}
            style={blob.style}
          />
        ))}
      </div>

      {/* Mesh gradient overlay */}
      {variant === 'mesh' && (
        <div className="absolute inset-0 bg-gradient-to-br from-violet-600/20 via-indigo-600/20 to-blue-600/20" />
      )}

      {/* Subtle noise texture */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        }}
      />
    </div>
  );
}
