'use client';

import { useState } from 'react';
import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Thermometer, CheckCircle, Clock, ListChecks } from 'lucide-react';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';
import { GradientText, CounterValue } from '@/components/animations';

export function StaffOverview() {
  const [todayTasks] = useState([
    { id: 1, task: 'Morning temperature check', completed: true, dueTime: '8:00 AM' },
    { id: 2, task: 'Cold storage inspection', completed: false, dueTime: '10:00 AM' },
    { id: 3, task: 'Hot holding verification', completed: false, dueTime: '12:00 PM' },
    { id: 4, task: 'Cleaning log', completed: false, dueTime: '2:00 PM' },
    { id: 5, task: 'Closing procedures', completed: false, dueTime: '10:00 PM' },
  ]);

  const completedCount = todayTasks.filter((t) => t.completed).length;
  const progressPercent = (completedCount / todayTasks.length) * 100;

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Progress Card */}
      <AnimatedPageWrapper animation="scale">
        <GlassCard variant="gradient" className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Today&apos;s Progress</CardTitle>
                <CardDescription>
                  {completedCount} of {todayTasks.length} tasks completed
                </CardDescription>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold">
                  <GradientText
                    variant={
                      progressPercent >= 80
                        ? 'success'
                        : progressPercent >= 50
                        ? 'warning'
                        : 'primary'
                    }
                  >
                    <CounterValue value={progressPercent} decimals={0} suffix="%" />
                  </GradientText>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="w-full bg-muted/50 rounded-full h-3 overflow-hidden">
              <div
                className="h-3 rounded-full transition-all duration-700 bg-gradient-to-r from-violet-500 via-indigo-500 to-emerald-500 relative"
                style={{ width: `${progressPercent}%` }}
              >
                <div className="absolute inset-0 shimmer" />
              </div>
            </div>
          </CardContent>
        </GlassCard>
      </AnimatedPageWrapper>

      {/* Quick Actions */}
      <AnimatedPageWrapper animation="stagger" staggerAmount={0.15}>
        <div className="grid gap-4 md:grid-cols-2">
          <GlassCard hover={true} className="stagger-item">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20">
                  <Thermometer className="h-8 w-8 text-blue-500" />
                </div>
                <div>
                  <p className="font-semibold">
                    <GradientText variant="cyan">Log Temperature</GradientText>
                  </p>
                  <p className="text-sm text-muted-foreground">Quick entry</p>
                </div>
              </div>
            </CardContent>
          </GlassCard>

          <GlassCard hover={true} className="stagger-item">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500/20 to-green-500/20">
                  <ListChecks className="h-8 w-8 text-emerald-500" />
                </div>
                <div>
                  <p className="font-semibold">
                    <GradientText variant="success">View Checklist</GradientText>
                  </p>
                  <p className="text-sm text-muted-foreground">All tasks</p>
                </div>
              </div>
            </CardContent>
          </GlassCard>
        </div>
      </AnimatedPageWrapper>
    </div>
  );
}

// Backward compatible export
export { StaffOverview as StaffDashboard };
