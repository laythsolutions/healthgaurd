'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, Clock, CheckCircle } from 'lucide-react';
import { GlassCard } from '@/components/layout/glass-card';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';
import { FloatingElement } from '@/components/animations';

interface AlertsListProps {
  restaurantId: string;
}

interface Alert {
  id: string;
  severity: string;
  message: string;
  created_at: string;
  status: string;
}

export function AlertsList({ restaurantId }: AlertsListProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Mock data for now
    const mockAlerts: Alert[] = [
      {
        id: '1',
        severity: 'critical',
        message: 'Temperature exceeded safe limit in Walk-in Cooler #1',
        created_at: new Date().toISOString(),
        status: 'active',
      },
      {
        id: '2',
        severity: 'warning',
        message: 'Door open for extended period (15 minutes)',
        created_at: new Date(Date.now() - 3600000).toISOString(),
        status: 'acknowledged',
      },
      {
        id: '3',
        severity: 'critical',
        message: 'Device "Hot Holding Station" has low battery (18%)',
        created_at: new Date(Date.now() - 7200000).toISOString(),
        status: 'active',
      },
    ];
    setAlerts(mockAlerts);
    setIsLoading(false);
  }, [restaurantId]);

  if (isLoading) {
    return <div className="text-muted-foreground">Loading alerts...</div>;
  }

  const getSeverityVariant = (severity: string) => {
    switch (severity) {
      case 'critical': return 'critical' as const;
      case 'warning': return 'warning' as const;
      default: return 'default' as const;
    }
  };

  return (
    <AnimatedPageWrapper animation="stagger" staggerAmount={0.15} className="space-y-4">
      {alerts.length === 0 ? (
        <GlassCard>
          <CardContent className="flex items-center justify-center h-32">
            <div className="text-center">
              <FloatingElement intensity="subtle">
                <CheckCircle className="h-12 w-12 text-emerald-500 mx-auto mb-3" />
              </FloatingElement>
              <p className="text-muted-foreground font-medium">No active alerts</p>
            </div>
          </CardContent>
        </GlassCard>
      ) : (
        alerts.map((alert, index) => (
          <GlassCard
            key={alert.id}
            className={`stagger-item card-lift ${
              alert.status === 'active' && alert.severity === 'critical'
                ? 'border-rose-500/50 hover:border-rose-500'
                : ''
            }`}
            style={{ animationDelay: `${index * 0.15}s` }}
          >
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <FloatingElement intensity="subtle">
                    <AlertTriangle
                      className={`h-5 w-5 ${
                        alert.severity === 'critical'
                          ? 'text-rose-500'
                          : 'text-amber-500'
                      }`}
                    />
                  </FloatingElement>
                  {alert.severity === 'critical' ? 'Critical' : 'Warning'}
                </CardTitle>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {new Date(alert.created_at).toLocaleTimeString()}
                  </div>
                  <Badge
                    variant={getSeverityVariant(alert.severity)}
                    pulse={alert.status === 'active' && alert.severity === 'critical'}
                  >
                    {alert.status}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm mb-3">{alert.message}</p>
              <div className="flex items-center justify-between">
                <span
                  className={`text-xs px-2 py-1 rounded-full font-medium status-badge ${
                    alert.severity === 'critical'
                      ? 'status-badge-critical'
                      : 'status-badge-warning'
                  }`}
                >
                  {alert.severity.toUpperCase()}
                </span>
                {alert.status === 'active' && (
                  <button className="text-xs bg-gradient-to-r from-violet-600 to-indigo-600 text-white px-3 py-1.5 rounded-lg hover:shadow-md transition-all">
                    Acknowledge
                  </button>
                )}
              </div>
            </CardContent>
          </GlassCard>
        ))
      )}
    </AnimatedPageWrapper>
  );
}
