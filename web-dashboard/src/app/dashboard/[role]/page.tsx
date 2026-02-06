'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Activity } from 'lucide-react';

/**
 * Role-based dashboard router
 * For development: redirects to role-specific dashboard
 * For production: will use user session to auto-route
 */
export default function RoleBasedDashboard({ params }: { params: { role: string } }) {
  const router = useRouter();

  useEffect(() => {
    // In production, this would redirect based on session.user.role
    // For now, just show the role-specific dashboard
    const role = params.role;

    // Validate role
    const validRoles = ['admin', 'manager', 'staff', 'inspector'];
    if (!validRoles.includes(role.toLowerCase())) {
      router.push('/');
      return;
    }
  }, [params.role, router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <Card className="w-96">
        <CardContent className="pt-6">
          <div className="flex items-center gap-3">
            <Activity className="h-6 w-6 animate-pulse" />
            <p>Loading dashboard...</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
