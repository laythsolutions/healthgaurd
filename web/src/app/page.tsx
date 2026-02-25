'use client';

import { Building2, Utensils, Users, ClipboardCheck } from 'lucide-react';
import { AnimatedBackground, GlassCard } from '@/components/layout';
import { AnimatedPageWrapper, StaggeredGrid } from '@/components/layout/animated-page-wrapper';
import { GradientText } from '@/components/animations';

const roles = [
  {
    href: '/dashboard/admin',
    icon: Building2,
    title: 'Admin',
    description: 'Organization-wide oversight, multi-restaurant management, user administration, billing',
    borderColor: 'border-l-violet-500',
    iconBg: 'from-violet-500/20 to-purple-500/20',
    iconColor: 'text-violet-500',
    glowColor: 'group-hover:shadow-[0_0_30px_rgba(139,92,246,0.3)]',
    badgeGradient: 'from-violet-500 to-purple-500',
    variant: 'primary' as const,
  },
  {
    href: '/dashboard/manager',
    icon: Utensils,
    title: 'Manager',
    description: 'Single restaurant operations, staff scheduling, task management, compliance reporting',
    borderColor: 'border-l-blue-500',
    iconBg: 'from-blue-500/20 to-cyan-500/20',
    iconColor: 'text-blue-500',
    glowColor: 'group-hover:shadow-[0_0_30px_rgba(59,130,246,0.3)]',
    badgeGradient: 'from-blue-500 to-cyan-500',
    variant: 'cyan' as const,
  },
  {
    href: '/dashboard/staff',
    icon: Users,
    title: 'Staff',
    description: 'Daily tasks, quick temperature logging, checklists, training materials',
    borderColor: 'border-l-emerald-500',
    iconBg: 'from-emerald-500/20 to-green-500/20',
    iconColor: 'text-emerald-500',
    glowColor: 'group-hover:shadow-[0_0_30px_rgba(16,185,129,0.3)]',
    badgeGradient: 'from-emerald-500 to-green-500',
    variant: 'success' as const,
  },
  {
    href: '/dashboard/inspector',
    icon: ClipboardCheck,
    title: 'Inspector',
    description: 'Inspection scheduling, violation tracking, compliance scoring, follow-up management',
    borderColor: 'border-l-orange-500',
    iconBg: 'from-orange-500/20 to-amber-500/20',
    iconColor: 'text-orange-500',
    glowColor: 'group-hover:shadow-[0_0_30px_rgba(249,115,22,0.3)]',
    badgeGradient: 'from-orange-500 to-amber-500',
    variant: 'warning' as const,
  },
];

export default function Home() {
  return (
    <div className="min-h-screen relative flex items-center justify-center p-4">
      <AnimatedBackground variant="gradient" intensity="high" />

      <AnimatedPageWrapper animation="scale" className="max-w-5xl w-full relative z-10">
        {/* Hero Title */}
        <div className="text-center mb-16">
          <h1 className="text-7xl md:text-8xl font-extrabold mb-6 tracking-tight">
            <span
              className="bg-gradient-to-r from-violet-500 via-indigo-500 to-cyan-500 bg-clip-text text-transparent animate-gradient-shift"
              style={{ backgroundSize: '200% 200%' }}
            >
              HealthGuard
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground font-medium max-w-2xl mx-auto">
            Automated restaurant compliance monitoring.{' '}
            <span className="text-foreground font-semibold">Real-time.</span>{' '}
            <span className="text-foreground font-semibold">Intelligent.</span>{' '}
            <span className="text-foreground font-semibold">Effortless.</span>
          </p>
        </div>

        {/* Role Cards Grid */}
        <StaggeredGrid cols={2} className="gap-6 mb-10">
          {roles.map((role) => {
            const Icon = role.icon;
            return (
              <a
                key={role.href}
                href={role.href}
                className="stagger-item"
              >
                <GlassCard
                  hover={true}
                  className={`p-6 h-full group border-l-4 ${role.borderColor} transition-all duration-300 hover:scale-[1.03] ${role.glowColor}`}
                >
                  <div className="flex items-center gap-4 mb-4">
                    <div className={`w-14 h-14 rounded-2xl flex items-center justify-center bg-gradient-to-br ${role.iconBg} group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className={`h-7 w-7 ${role.iconColor}`} />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold">
                        <GradientText variant={role.variant}>{role.title} Dashboard</GradientText>
                      </h3>
                      <span className={`inline-block px-2.5 py-0.5 text-[10px] bg-gradient-to-r ${role.badgeGradient} text-white rounded-full font-bold uppercase tracking-wider`}>
                        {role.title}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {role.description}
                  </p>
                </GlassCard>
              </a>
            );
          })}
        </StaggeredGrid>

        {/* Note */}
        <div className="p-4 rounded-xl backdrop-blur-lg bg-muted/30 border border-white/10">
          <p className="text-sm text-muted-foreground text-center">
            <strong>Demo Mode:</strong> In production, users are automatically routed based on their authenticated role.
          </p>
        </div>
      </AnimatedPageWrapper>
    </div>
  );
}
