'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AlertTriangle, Clock, CheckCircle, X, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useGSAP, usePulseAnimation } from '@/hooks/use-gsap';

interface AlertsListProps {
  restaurantId: string;
  limit?: number;
}

interface Alert {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  created_at: string;
  status: 'active' | 'acknowledged' | 'resolved';
  device_name?: string;
  location?: string;
}

const severityConfig = {
  critical: {
    icon: AlertTriangle,
    color: 'text-red-500',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/20',
    pulse: true,
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/20',
    pulse: false,
  },
  info: {
    icon: AlertTriangle,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/20',
    pulse: false,
  },
};

const statusConfig = {
  active: {
    label: 'Active',
    color: 'bg-red-500/10 text-red-500',
    icon: AlertTriangle,
  },
  acknowledged: {
    label: 'Acknowledged',
    color: 'bg-yellow-500/10 text-yellow-500',
    icon: Clock,
  },
  resolved: {
    label: 'Resolved',
    color: 'bg-green-500/10 text-green-500',
    icon: CheckCircle,
  },
};

export function AlertsListEnhanced({ restaurantId, limit = 10 }: AlertsListProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'active' | 'resolved'>('all');

  useEffect(() => {
    // Mock data
    const mockAlerts: Alert[] = [
      {
        id: '1',
        severity: 'critical',
        title: 'Temperature Critical',
        message: 'Walk-in cooler temperature exceeded safe limit (48°F)',
        created_at: new Date().toISOString(),
        status: 'active',
        device_name: 'Sensor TC-001',
        location: 'Kitchen - Walk-in Cooler',
      },
      {
        id: '2',
        severity: 'warning',
        title: 'Door Open Too Long',
        message: 'Back door has been open for 5 minutes',
        created_at: new Date(Date.now() - 3600000).toISOString(),
        status: 'active',
        device_name: 'Door Sensor DS-002',
        location: 'Back Entrance',
      },
      {
        id: '3',
        severity: 'critical',
        title: 'Device Offline',
        message: 'Temperature sensor stopped responding',
        created_at: new Date(Date.now() - 7200000).toISOString(),
        status: 'acknowledged',
        device_name: 'Sensor TC-003',
        location: 'Storage Room',
      },
      {
        id: '4',
        severity: 'warning',
        title: 'High Humidity',
        message: 'Humidity levels above optimal range (75%)',
        created_at: new Date(Date.now() - 10800000).toISOString(),
        status: 'resolved',
        device_name: 'Sensor HS-001',
        location: 'Dry Storage',
      },
      {
        id: '5',
        severity: 'info',
        title: 'Battery Low',
        message: 'Sensor battery at 15% capacity',
        created_at: new Date(Date.now() - 14400000).toISOString(),
        status: 'active',
        device_name: 'Sensor TC-004',
        location: 'Freezer',
      },
    ];
    setAlerts(mockAlerts);
    setIsLoading(false);
  }, [restaurantId]);

  const filteredAlerts = alerts.filter((alert) => {
    if (filter === 'active') return alert.status === 'active';
    if (filter === 'resolved') return alert.status === 'resolved';
    return true;
  });

  const displayedAlerts = limit ? filteredAlerts.slice(0, limit) : filteredAlerts;

  const handleAcknowledge = (id: string) => {
    setAlerts((prev) =>
      prev.map((alert) =>
        alert.id === id ? { ...alert, status: 'acknowledged' as const } : alert
      )
    );
  };

  const handleResolve = (id: string) => {
    setAlerts((prev) =>
      prev.map((alert) =>
        alert.id === id ? { ...alert, status: 'resolved' as const } : alert
      )
    );
  };

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="p-4 animate-pulse">
            <div className="h-4 bg-muted rounded w-3/4 mb-2" />
            <div className="h-3 bg-muted rounded w-1/2" />
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-2">
        <Button
          variant={filter === 'all' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setFilter('all')}
        >
          All ({alerts.length})
        </Button>
        <Button
          variant={filter === 'active' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setFilter('active')}
        >
          Active ({alerts.filter((a) => a.status === 'active').length})
        </Button>
        <Button
          variant={filter === 'resolved' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setFilter('resolved')}
        >
          Resolved ({alerts.filter((a) => a.status === 'resolved').length})
        </Button>
      </div>

      {/* Alerts List */}
      <div className="space-y-3 stagger-item">
        {displayedAlerts.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <CheckCircle className="h-16 w-16 text-green-500 mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Alerts</h3>
              <p className="text-sm text-muted-foreground text-center">
                {filter === 'active'
                  ? 'Great! No active alerts requiring attention.'
                  : 'No alerts found matching your filter.'}
              </p>
            </CardContent>
          </Card>
        ) : (
          displayedAlerts.map((alert, index) => {
            const config = severityConfig[alert.severity];
            const statusInfo = statusConfig[alert.status];
            const StatusIcon = statusInfo.icon;
            const SeverityIcon = config.icon;

            return (
              <AlertCard
                key={alert.id}
                alert={alert}
                config={config}
                statusInfo={statusInfo}
                StatusIcon={StatusIcon}
                SeverityIcon={SeverityIcon}
                onAcknowledge={() => handleAcknowledge(alert.id)}
                onResolve={() => handleResolve(alert.id)}
                delay={index * 0.1}
              />
            );
          })
        )}
      </div>
    </div>
  );
}

// Individual Alert Card Component
function AlertCard({
  alert,
  config,
  statusInfo,
  StatusIcon,
  SeverityIcon,
  onAcknowledge,
  onResolve,
  delay,
}: {
  alert: Alert;
  config: typeof severityConfig.critical;
  statusInfo: typeof statusConfig.active;
  StatusIcon: React.ElementType;
  SeverityIcon: React.ElementType;
  onAcknowledge: () => void;
  onResolve: () => void;
  delay: number;
}) {
  const cardRef = usePulseAnimation(alert.status === 'active' && alert.severity === 'critical');

  return (
    <Card
      ref={cardRef}
      className={cn(
        'group hover:shadow-md transition-all duration-300 border-l-4',
        config.borderColor,
        config.bgColor
      )}
      style={{
        animationDelay: `${delay}s`,
      }}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className={cn('p-2 rounded-full', config.bgColor)}>
            <SeverityIcon className={cn('h-5 w-5', config.color)} />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-semibold text-sm">{alert.title}</h4>
              <Badge className={statusInfo.color} variant="secondary">
                <StatusIcon className="h-3 w-3 mr-1" />
                {statusInfo.label}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mb-2">{alert.message}</p>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {new Date(alert.created_at).toLocaleString()}
              </span>
              {alert.device_name && (
                <>
                  <span>•</span>
                  <span>{alert.device_name}</span>
                </>
              )}
              {alert.location && (
                <>
                  <span>•</span>
                  <span>{alert.location}</span>
                </>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            {alert.status === 'active' && (
              <Button
                size="sm"
                variant="outline"
                onClick={onAcknowledge}
                className="h-8"
              >
                Acknowledge
              </Button>
            )}
            {alert.status === 'acknowledged' && (
              <Button
                size="sm"
                variant="outline"
                onClick={onResolve}
                className="h-8"
              >
                Resolve
              </Button>
            )}
            <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
