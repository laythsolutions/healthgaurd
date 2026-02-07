'use client';

import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';
import { GradientText } from '@/components/animations';

export function StaffAlerts() {
  return (
    <AnimatedPageWrapper animation="fade">
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Recent Alerts</CardTitle>
          <CardDescription>Notifications relevant to you</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="p-4 rounded-lg bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 card-lift">
              <p className="font-semibold">
                <GradientText variant="warning">Hot Holding Temperature</GradientText>
              </p>
              <p className="text-sm text-muted-foreground">Hot holding is at 145°F (should be above 135°F)</p>
              <p className="text-xs text-muted-foreground mt-2">5 minutes ago</p>
              <span className="status-badge status-badge-warning mt-2">warning</span>
            </div>
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
