'use client';

import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';

export function AdminUsers() {
  return (
    <AnimatedPageWrapper animation="fade">
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>User Management</CardTitle>
          <CardDescription>Manage team members and permissions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { name: 'Maria Santos', role: 'Manager', location: 'Downtown Location', status: 'active' },
              { name: 'John Davis', role: 'Staff', location: 'Midtown Branch', status: 'active' },
              { name: 'Ahmed Khan', role: 'Staff', location: 'Downtown Location', status: 'active' },
              { name: 'Sarah Wilson', role: 'Manager', location: 'Uptown Bistro', status: 'inactive' },
            ].map((user) => (
              <div key={user.name} className="p-4 border rounded-lg flex items-center justify-between card-lift bg-gradient-to-r from-background to-muted/20">
                <div>
                  <p className="font-medium">{user.name}</p>
                  <p className="text-sm text-muted-foreground">{user.role} &bull; {user.location}</p>
                </div>
                <span className={`status-badge ${user.status === 'active' ? 'status-badge-success' : 'status-badge-warning'}`}>
                  {user.status}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
