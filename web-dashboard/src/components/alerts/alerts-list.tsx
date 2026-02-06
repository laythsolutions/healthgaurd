'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, Clock, CheckCircle } from 'lucide-react';

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
        message: 'Temperature exceeded safe limit',
        created_at: new Date().toISOString(),
        status: 'active',
      },
      {
        id: '2',
        severity: 'warning',
        message: 'Door open for extended period',
        created_at: new Date(Date.now() - 3600000).toISOString(),
        status: 'acknowledged',
      },
    ];
    setAlerts(mockAlerts);
    setIsLoading(false);
  }, [restaurantId]);

  if (isLoading) {
    return <div className="text-muted-foreground">Loading alerts...</div>;
  }

  return (
    <div className="space-y-4">
      {alerts.length === 0 ? (
        <Card>
          <CardContent className="flex items-center justify-center h-32">
            <div className="text-center">
              <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
              <p className="text-muted-foreground">No active alerts</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        alerts.map((alert) => (
          <Card key={alert.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <AlertTriangle
                    className={`h-4 w-4 ${
                      alert.severity === 'critical'
                        ? 'text-destructive'
                        : 'text-yellow-500'
                    }`}
                  />
                  {alert.severity === 'critical' ? 'Critical' : 'Warning'}
                </CardTitle>
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  {new Date(alert.created_at).toLocaleTimeString()}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p>{alert.message}</p>
              <div className="mt-2">
                <span
                  className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                    alert.status === 'active'
                      ? 'bg-destructive/10 text-destructive'
                      : 'bg-green-500/10 text-green-500'
                  }`}
                >
                  {alert.status}
                </span>
              </div>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}
