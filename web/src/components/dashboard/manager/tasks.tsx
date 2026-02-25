'use client';

import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';

export function ManagerTasks() {
  return (
    <AnimatedPageWrapper animation="fade">
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Today&apos;s Tasks</CardTitle>
          <CardDescription>Daily compliance checklist and assignments</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { task: 'Morning temperature check', assigned: 'Maria S.', status: 'complete', time: '8:00 AM' },
              { task: 'Cold storage inspection', assigned: 'John D.', status: 'pending', time: '10:00 AM' },
              { task: 'Hot holding verification', assigned: 'Maria S.', status: 'pending', time: '12:00 PM' },
              { task: 'Closing procedures', assigned: 'Ahmed K.', status: 'pending', time: '10:00 PM' },
            ].map((task, index) => (
              <div
                key={task.task}
                className="p-4 border rounded-lg flex items-center justify-between card-lift stagger-item"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${
                    task.status === 'complete' ? 'bg-emerald-500 glow-emerald' :
                    task.status === 'in-progress' ? 'bg-amber-500 glow-amber' :
                    'bg-gray-300'
                  }`} />
                  <div>
                    <p className="font-medium">{task.task}</p>
                    <p className="text-sm text-muted-foreground">
                      Assigned to {task.assigned} &bull; {task.time}
                    </p>
                  </div>
                </div>
                <span className={`status-badge ${
                  task.status === 'complete' ? 'status-badge-success' :
                  task.status === 'in-progress' ? 'status-badge-warning' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {task.status}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
