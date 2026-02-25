'use client';

import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper, StaggeredGrid } from '@/components/layout/animated-page-wrapper';
import { GradientText } from '@/components/animations';

export function StaffSensors() {
  return (
    <AnimatedPageWrapper animation="stagger" staggerAmount={0.1}>
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Quick Temperature Check</CardTitle>
          <CardDescription>Verify sensor readings</CardDescription>
        </CardHeader>
        <CardContent>
          <StaggeredGrid cols={2}>
            {[
              { sensor: 'Walk-in Cooler', current: '36', unit: '°F', status: 'ok' },
              { sensor: 'Walk-in Freezer', current: '-2', unit: '°F', status: 'ok' },
              { sensor: 'Hot Holding', current: '145', unit: '°F', status: 'warning' },
              { sensor: 'Cold Holding', current: '38', unit: '°F', status: 'ok' },
            ].map((sensor) => (
              <div
                key={sensor.sensor}
                className={`p-4 border rounded-lg stagger-item card-lift ${
                  sensor.status === 'ok'
                    ? 'border-emerald-500/30 bg-gradient-to-br from-emerald-500/5 to-green-500/5'
                    : 'border-rose-500/30 bg-gradient-to-br from-rose-500/5 to-red-500/5'
                }`}
              >
                <p className="font-medium text-sm mb-1">{sensor.sensor}</p>
                <p className="text-2xl font-bold">
                  <GradientText variant={sensor.status === 'ok' ? 'success' : 'critical'}>
                    {sensor.current}{sensor.unit}
                  </GradientText>
                </p>
                <span className={`status-badge mt-2 ${
                  sensor.status === 'ok' ? 'status-badge-success' : 'status-badge-critical'
                }`}>
                  {sensor.status === 'ok' ? 'Normal' : 'Check'}
                </span>
              </div>
            ))}
          </StaggeredGrid>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
