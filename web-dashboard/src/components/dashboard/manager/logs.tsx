'use client';

import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';

export function ManagerLogs() {
  return (
    <AnimatedPageWrapper animation="stagger" staggerAmount={0.15}>
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Manual Logs Review</CardTitle>
          <CardDescription>Review and approve staff entries</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { type: 'Temperature', staff: 'Maria S.', time: '2:30 PM', value: '38°F', status: 'approved' },
              { type: 'Temperature', staff: 'John D.', time: '3:15 PM', value: '165°F', status: 'pending' },
              { type: 'Receiving', staff: 'Ahmed K.', time: '11:00 AM', value: 'Fresh delivery', status: 'approved' },
            ].map((log, index) => (
              <div
                key={`${log.staff}-${log.time}`}
                className="p-4 border rounded-lg flex items-center justify-between card-lift bg-gradient-to-r from-background to-muted/20 stagger-item"
                style={{ animationDelay: `${index * 0.15}s` }}
              >
                <div>
                  <p className="font-medium">{log.type} Log</p>
                  <p className="text-sm text-muted-foreground">
                    {log.staff} &bull; {log.time} &bull; {log.value}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`status-badge ${log.status === 'approved' ? 'status-badge-success' : 'status-badge-warning'}`}>
                    {log.status}
                  </span>
                  {log.status === 'pending' && (
                    <button className="text-xs bg-gradient-to-r from-violet-600 to-indigo-600 text-white px-3 py-1.5 rounded-lg hover:shadow-md transition-all">
                      Review
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
