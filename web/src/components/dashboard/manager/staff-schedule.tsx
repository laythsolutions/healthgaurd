'use client';

import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper, StaggeredGrid } from '@/components/layout/animated-page-wrapper';

export function ManagerStaffSchedule() {
  return (
    <AnimatedPageWrapper animation="stagger" staggerAmount={0.1}>
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Staff Schedule</CardTitle>
          <CardDescription>Manage shifts and assignments</CardDescription>
        </CardHeader>
        <CardContent>
          <StaggeredGrid cols={3}>
            {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
              <div key={day} className="border rounded-lg p-4 card-lift bg-gradient-to-br from-background to-muted/30">
                <p className="font-semibold mb-3 text-lg">{day}</p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full glow-emerald" />
                    <span>Maria S.</span>
                    <span className="text-muted-foreground text-xs">8AM-4PM</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full glow-cyan" />
                    <span>John D.</span>
                    <span className="text-muted-foreground text-xs">4PM-12AM</span>
                  </div>
                </div>
              </div>
            ))}
          </StaggeredGrid>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
