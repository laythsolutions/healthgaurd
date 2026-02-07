'use client';

import { useState } from 'react';
import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Building2, Users, TrendingUp, DollarSign } from 'lucide-react';
import { GlassCard } from '@/components/layout';
import { KPICard } from './kpi-card';
import { AnimatedPageWrapper, StaggeredGrid } from '@/components/layout/animated-page-wrapper';
import { GradientText } from '@/components/animations';

export function AdminOverview() {
  const [stats] = useState({
    totalRestaurants: 12,
    totalUsers: 48,
    avgComplianceScore: 91.7,
    monthlyRevenue: 14388,
  });

  return (
    <div className="space-y-8">
      {/* KPI Cards */}
      <AnimatedPageWrapper animation="stagger" staggerAmount={0.1} delay={0.2}>
        <StaggeredGrid cols={4} className="gap-4">
          <KPICard
            title="Total Restaurants"
            value={stats.totalRestaurants}
            icon={Building2}
            status="neutral"
            decimals={0}
            description="Across all regions"
            trend={8.3}
            variant="glass"
          />
          <KPICard
            title="Total Users"
            value={stats.totalUsers}
            icon={Users}
            status="good"
            decimals={0}
            description="Active team members"
            trend={12.5}
            variant="glass"
          />
          <KPICard
            title="Avg Compliance"
            value={stats.avgComplianceScore}
            icon={TrendingUp}
            status="good"
            suffix="%"
            decimals={1}
            description="Organization-wide"
            trend={3.2}
            variant="glass"
          />
          <KPICard
            title="Monthly Revenue"
            value={stats.monthlyRevenue}
            icon={DollarSign}
            status="good"
            prefix="$"
            decimals={0}
            description="Recurring MRR"
            trend={5.1}
            variant="glass"
          />
        </StaggeredGrid>
      </AnimatedPageWrapper>

      {/* Restaurant Summary */}
      <AnimatedPageWrapper animation="fade">
        <GlassCard variant="default">
          <CardHeader>
            <CardTitle>Restaurant Portfolio</CardTitle>
            <CardDescription>Quick overview of all locations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { name: 'Downtown Location', score: 94.5, status: 'excellent', alerts: 0 },
                { name: 'Midtown Branch', score: 88.2, status: 'good', alerts: 2 },
                { name: 'Uptown Bistro', score: 76.8, status: 'attention', alerts: 5 },
                { name: 'Suburban Cafe', score: 91.3, status: 'good', alerts: 1 },
              ].map((restaurant) => (
                <div
                  key={restaurant.name}
                  className="p-4 border rounded-lg flex items-center justify-between card-lift bg-gradient-to-r from-background to-muted/20"
                >
                  <div className="flex-1">
                    <p className="font-medium">{restaurant.name}</p>
                    <p className="text-sm text-muted-foreground">
                      Compliance:{' '}
                      <GradientText
                        variant={
                          restaurant.score >= 90
                            ? 'success'
                            : restaurant.score >= 80
                            ? 'warning'
                            : 'critical'
                        }
                      >
                        {restaurant.score}%
                      </GradientText>
                    </p>
                  </div>
                  <div className="text-right flex items-center gap-3">
                    <div>
                      <p className="text-sm">{restaurant.alerts} alerts</p>
                      <span
                        className={`status-badge ${
                          restaurant.status === 'excellent' || restaurant.status === 'good'
                            ? 'status-badge-success'
                            : 'status-badge-warning'
                        }`}
                      >
                        {restaurant.status}
                      </span>
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
export { AdminOverview as AdminDashboard };
