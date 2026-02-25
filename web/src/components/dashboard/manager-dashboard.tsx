'use client';

import { useState, useEffect } from 'react';
import { CheckCircle, Users, AlertTriangle, Thermometer } from 'lucide-react';
import { KPICard } from './kpi-card';
import { AnimatedPageWrapper, StaggeredGrid } from '@/components/layout/animated-page-wrapper';

export function ManagerOverview() {
  const [stats, setStats] = useState({
    complianceScore: 94.5,
    staffOnDuty: 5,
    pendingTasks: 7,
    weeklyAlerts: 3,
    avgTemperature: 38.2,
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setStats((prev) => ({
        ...prev,
        avgTemperature: 35 + Math.random() * 10,
      }));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-8">
      <AnimatedPageWrapper animation="stagger" staggerAmount={0.1} delay={0.2}>
        <StaggeredGrid cols={4} className="gap-4">
          <KPICard
            title="Compliance Score"
            value={stats.complianceScore}
            icon={CheckCircle}
            status="good"
            suffix="%"
            decimals={1}
            description="Overall score"
            trend={2.5}
            variant="glass"
          />
          <KPICard
            title="Staff on Duty"
            value={stats.staffOnDuty}
            icon={Users}
            status="neutral"
            description={`${stats.pendingTasks} pending tasks`}
            trend={-1}
            variant="glass"
          />
          <KPICard
            title="Weekly Alerts"
            value={stats.weeklyAlerts}
            icon={AlertTriangle}
            status={stats.weeklyAlerts > 5 ? 'critical' : 'warning'}
            description="This week"
            trend={-15}
            variant="glass"
          />
          <KPICard
            title="Avg Temperature"
            value={stats.avgTemperature}
            icon={Thermometer}
            status="neutral"
            suffix="°F"
            decimals={1}
            description="All sensors"
            variant="glass"
          />
        </StaggeredGrid>
      </AnimatedPageWrapper>
    </div>
  );
}

// Backward compatible export
export { ManagerOverview as ManagerDashboard };
