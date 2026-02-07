'use client';

import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';
import { GradientText } from '@/components/animations';

export function InspectorFollowups() {
  return (
    <AnimatedPageWrapper animation="stagger" staggerAmount={0.1}>
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Scheduled Follow-ups</CardTitle>
          <CardDescription>Re-inspections for critical violations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { restaurant: 'Suburban Grill', violation: 'Cold holding', followupDate: '2024-02-10', daysRemaining: 3 },
              { restaurant: 'Midtown Diner', violation: 'Sanitizing', followupDate: '2024-02-12', daysRemaining: 5 },
            ].map((followup, idx) => (
              <div
                key={idx}
                className="p-4 rounded-lg bg-gradient-to-r from-orange-500/10 to-amber-500/10 border border-orange-500/20 card-lift stagger-item"
              >
                <p className="font-semibold">
                  <GradientText variant="warning">{followup.restaurant}</GradientText>
                </p>
                <p className="text-sm text-muted-foreground">Violation: {followup.violation}</p>
                <p className="text-sm text-muted-foreground">
                  Follow-up: {followup.followupDate}
                  <span className="ml-2 status-badge status-badge-warning">{followup.daysRemaining} days</span>
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
