'use client';

import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';

export function InspectorViolations() {
  return (
    <AnimatedPageWrapper animation="fade">
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Violation Tracking</CardTitle>
          <CardDescription>Track and follow up on violations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { restaurant: 'Suburban Grill', violation: 'Cold holding at 45°F', date: '2024-01-30', status: 'pending' },
              { restaurant: 'Downtown Bistro', violation: 'No hot water', date: '2024-02-03', status: 'resolved' },
              { restaurant: 'Midtown Diner', violation: 'Improper sanitizing', date: '2024-02-05', status: 'pending' },
            ].map((v, idx) => (
              <div key={idx} className="p-4 border rounded-lg flex items-center justify-between card-lift">
                <div className="flex-1">
                  <p className="font-medium">{v.restaurant}</p>
                  <p className="text-sm text-muted-foreground">{v.violation}</p>
                  <p className="text-xs text-muted-foreground">{v.date}</p>
                </div>
                <span className={`status-badge ${v.status === 'resolved' ? 'status-badge-success' : 'status-badge-warning'}`}>
                  {v.status}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
