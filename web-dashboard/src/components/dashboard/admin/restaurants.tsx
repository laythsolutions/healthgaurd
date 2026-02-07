'use client';

import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';
import { GradientText } from '@/components/animations';

export function AdminRestaurants() {
  return (
    <AnimatedPageWrapper animation="fade">
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Restaurant Portfolio</CardTitle>
          <CardDescription>Manage all restaurants in your organization</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { name: 'Downtown Location', score: 94.5, status: 'excellent', alerts: 0 },
              { name: 'Midtown Branch', score: 88.2, status: 'good', alerts: 2 },
              { name: 'Uptown Bistro', score: 76.8, status: 'attention', alerts: 5 },
              { name: 'Suburban Cafe', score: 91.3, status: 'good', alerts: 1 },
            ].map((restaurant, index) => (
              <div
                key={restaurant.name}
                className="p-4 border rounded-lg flex items-center justify-between card-lift bg-gradient-to-r from-background to-muted/20 stagger-item"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="flex-1">
                  <p className="font-medium">{restaurant.name}</p>
                  <p className="text-sm text-muted-foreground">
                    Compliance:{' '}
                    <GradientText variant={restaurant.score >= 90 ? 'success' : restaurant.score >= 80 ? 'warning' : 'critical'}>
                      {restaurant.score}%
                    </GradientText>
                  </p>
                </div>
                <div className="text-right flex items-center gap-3">
                  <div>
                    <p className="text-sm">{restaurant.alerts} alerts</p>
                    <span className={`status-badge ${restaurant.status === 'excellent' || restaurant.status === 'good' ? 'status-badge-success' : 'status-badge-warning'}`}>
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
  );
}
