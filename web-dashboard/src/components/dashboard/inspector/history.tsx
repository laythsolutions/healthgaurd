'use client';

import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';
import { GradientText } from '@/components/animations';

export function InspectorHistory() {
  return (
    <AnimatedPageWrapper animation="fade">
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Inspection History</CardTitle>
          <CardDescription>Your past inspections</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { restaurant: 'Midtown Diner', date: '2024-02-05', score: 92, violations: 1 },
              { restaurant: 'Downtown Bistro', date: '2024-02-03', score: 88, violations: 3 },
              { restaurant: 'Uptown Cafe', date: '2024-02-01', score: 95, violations: 0 },
              { restaurant: 'Suburban Grill', date: '2024-01-30', score: 76, violations: 5 },
            ].map((inspection, idx) => (
              <div key={idx} className="p-4 border rounded-lg flex items-center justify-between card-lift">
                <div className="flex-1">
                  <p className="font-medium">{inspection.restaurant}</p>
                  <p className="text-sm text-muted-foreground">{inspection.date}</p>
                </div>
                <div className="text-right flex items-center gap-3">
                  <div>
                    <p className="text-2xl font-bold">
                      <GradientText variant={
                        inspection.score >= 90 ? 'success' :
                        inspection.score >= 80 ? 'warning' :
                        'critical'
                      }>
                        {inspection.score}
                      </GradientText>
                    </p>
                    <p className="text-xs text-muted-foreground">{inspection.violations} violations</p>
                  </div>
                  <span className={`status-badge ${
                    inspection.score >= 90 ? 'status-badge-success' :
                    inspection.score >= 80 ? 'status-badge-warning' :
                    'status-badge-critical'
                  }`}>
                    {inspection.score >= 90 ? 'pass' :
                     inspection.score >= 80 ? 'marginal' :
                     'fail'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
