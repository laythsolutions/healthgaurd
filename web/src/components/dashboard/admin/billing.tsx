'use client';

import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';

export function AdminBilling() {
  return (
    <AnimatedPageWrapper animation="fade">
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Billing &amp; Subscriptions</CardTitle>
          <CardDescription>Manage payment methods and invoices</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 border rounded-lg card-lift bg-gradient-to-r from-background to-muted/20">
              <div className="flex items-center justify-between mb-2">
                <p className="font-semibold">Current Plan</p>
                <span className="status-badge status-badge-success">Active</span>
              </div>
              <p className="text-2xl font-bold">$199<span className="text-sm font-normal text-muted-foreground">/month per location</span></p>
              <p className="text-sm text-muted-foreground mt-1">12 locations &bull; Next billing: March 1, 2024</p>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <div className="p-4 border rounded-lg card-lift bg-gradient-to-br from-background to-muted/30">
                <p className="font-medium">Monthly Total</p>
                <p className="text-xl font-bold">$2,388</p>
              </div>
              <div className="p-4 border rounded-lg card-lift bg-gradient-to-br from-background to-muted/30">
                <p className="font-medium">Annual Savings</p>
                <p className="text-xl font-bold text-emerald-500">$2,868</p>
              </div>
            </div>
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
