'use client';

import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';

export function AdminSettings() {
  return (
    <AnimatedPageWrapper animation="fade">
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Organization Settings</CardTitle>
          <CardDescription>Configure organization-wide settings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { label: 'Organization Name', value: 'HealthGuard Demo Corp' },
              { label: 'Default Alert Threshold', value: '85% compliance score' },
              { label: 'Report Frequency', value: 'Weekly' },
              { label: 'Notification Channels', value: 'Email, SMS, Push' },
            ].map((setting) => (
              <div key={setting.label} className="p-4 border rounded-lg flex items-center justify-between card-lift bg-gradient-to-r from-background to-muted/20">
                <div>
                  <p className="font-medium">{setting.label}</p>
                  <p className="text-sm text-muted-foreground">{setting.value}</p>
                </div>
                <button className="text-xs bg-secondary px-3 py-1.5 rounded hover:bg-secondary/80 transition-all">Edit</button>
              </div>
            ))}
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
