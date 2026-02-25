'use client';

import { useState } from 'react';
import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ClipboardCheck, FileText, AlertTriangle, TrendingDown, MapPin } from 'lucide-react';
import { GlassCard } from '@/components/layout';
import { KPICard } from './kpi-card';
import { AnimatedPageWrapper, StaggeredGrid } from '@/components/layout/animated-page-wrapper';
import { GradientText } from '@/components/animations';

export function InspectorOverview() {
  const [scheduledInspections] = useState([
    { id: 1, restaurant: 'Downtown Bistro', address: '123 Main St', date: '2024-02-07', time: '10:00 AM', priority: 'high' as const },
    { id: 2, restaurant: 'Uptown Cafe', address: '456 Oak Ave', date: '2024-02-07', time: '2:00 PM', priority: 'normal' as const },
    { id: 3, restaurant: 'Midtown Diner', address: '789 Elm St', date: '2024-02-08', time: '9:00 AM', priority: 'normal' as const },
  ]);

  return (
    <div className="space-y-8">
      {/* KPI Cards */}
      <AnimatedPageWrapper animation="stagger" staggerAmount={0.1} delay={0.2}>
        <StaggeredGrid cols={4} className="gap-4">
          <KPICard
            title="Today's Inspections"
            value={scheduledInspections.length}
            icon={ClipboardCheck}
            status="neutral"
            decimals={0}
            description="Scheduled"
            variant="glass"
          />
          <KPICard
            title="Completed This Week"
            value={24}
            icon={FileText}
            status="good"
            decimals={0}
            description="Inspections"
            trend={8.0}
            variant="glass"
          />
          <KPICard
            title="Critical Violations"
            value={3}
            icon={AlertTriangle}
            status="critical"
            decimals={0}
            description="This week"
            trend={-25.0}
            variant="glass"
          />
          <KPICard
            title="Avg Score Given"
            value={87.3}
            icon={TrendingDown}
            status="warning"
            decimals={1}
            description="This month"
            trend={-2.1}
            variant="glass"
          />
        </StaggeredGrid>
      </AnimatedPageWrapper>

      {/* Today's Schedule Summary */}
      <AnimatedPageWrapper animation="fade">
        <GlassCard variant="default">
          <CardHeader>
            <CardTitle>Today&apos;s Schedule</CardTitle>
            <CardDescription>Upcoming inspections</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {scheduledInspections.map((inspection) => (
                <div
                  key={inspection.id}
                  className="p-4 border rounded-lg card-lift bg-gradient-to-r from-background to-muted/20"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold">
                          <GradientText variant="warning">{inspection.restaurant}</GradientText>
                        </h3>
                        {inspection.priority === 'high' && (
                          <span className="status-badge status-badge-critical animate-pulse">
                            PRIORITY
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {inspection.address}
                      </p>
                    </div>
                    <div className="text-sm text-right">
                      <p className="font-medium">{inspection.time}</p>
                      <p className="text-muted-foreground">{inspection.date}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </GlassCard>
      </AnimatedPageWrapper>
    </div>
  );
}

// Backward compatible export
export { InspectorOverview as InspectorDashboard };
