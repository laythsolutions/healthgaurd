'use client';

import { AlertTriangle } from 'lucide-react';
import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';
import { GradientText } from '@/components/animations';

export function AdminAlerts() {
  return (
    <AnimatedPageWrapper animation="stagger" staggerAmount={0.1}>
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>System Alerts</CardTitle>
          <CardDescription>Critical issues across all locations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="p-4 rounded-lg flex items-start gap-3 bg-gradient-to-r from-rose-500/10 to-red-500/10 border border-rose-500/20 stagger-item card-lift">
              <AlertTriangle className="h-5 w-5 text-rose-500 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold">
                  <GradientText variant="critical">Critical: Uptown Bistro</GradientText>
                </p>
                <p className="text-sm text-muted-foreground">Temperature sensor offline for 2+ hours</p>
              </div>
              <button className="px-3 py-1.5 text-xs bg-gradient-to-r from-rose-600 to-red-600 text-white rounded-lg hover:shadow-md transition-all">
                Respond
              </button>
            </div>
            <div className="p-4 rounded-lg flex items-start gap-3 bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 stagger-item card-lift">
              <AlertTriangle className="h-5 w-5 text-amber-500 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold">
                  <GradientText variant="warning">Warning: Midtown Branch</GradientText>
                </p>
                <p className="text-sm text-muted-foreground">Compliance score dropped below 85%</p>
              </div>
              <button className="px-3 py-1.5 text-xs bg-gradient-to-r from-amber-600 to-orange-600 text-white rounded-lg hover:shadow-md transition-all">
                Respond
              </button>
            </div>
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
