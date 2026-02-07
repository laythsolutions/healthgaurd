'use client';

import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';

export function AdminAnalytics() {
  return (
    <AnimatedPageWrapper animation="fade">
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Organization Analytics</CardTitle>
          <CardDescription>Performance trends and insights across all locations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {[
              { title: 'Compliance Trends', desc: 'Average compliance scores trending upward across all locations over the past 30 days.' },
              { title: 'Alert Distribution', desc: 'Temperature alerts down 15% from last month. Cleaning alerts stable.' },
              { title: 'Staff Performance', desc: 'Task completion rate at 87% average across all locations.' },
              { title: 'Device Health', desc: '98.5% sensor uptime. 2 devices need maintenance.' },
            ].map((item) => (
              <div key={item.title} className="p-4 border rounded-lg card-lift bg-gradient-to-br from-background to-muted/30">
                <p className="font-semibold mb-2">{item.title}</p>
                <p className="text-sm text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
