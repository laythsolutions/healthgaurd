'use client';

import { Clock } from 'lucide-react';
import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';

export function StaffTraining() {
  return (
    <AnimatedPageWrapper animation="fade">
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Training Materials</CardTitle>
          <CardDescription>Learn proper food safety procedures</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { title: 'Temperature Logging 101', duration: '5 min', completed: true },
              { title: 'Cold Storage Guidelines', duration: '8 min', completed: true },
              { title: 'Hot Holding Procedures', duration: '6 min', completed: false },
              { title: 'Cross-Contamination Prevention', duration: '10 min', completed: false },
            ].map((training) => (
              <div key={training.title} className="p-4 border rounded-lg flex items-center justify-between card-lift">
                <div>
                  <p className="font-medium">{training.title}</p>
                  <p className="text-sm text-muted-foreground">
                    <Clock className="h-3 w-3 inline mr-1" />
                    {training.duration}
                  </p>
                </div>
                <button className={`text-sm px-3 py-1.5 rounded-lg transition-all ${
                  training.completed
                    ? 'status-badge status-badge-success'
                    : 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white hover:shadow-md'
                }`}>
                  {training.completed ? 'Completed' : 'Start'}
                </button>
              </div>
            ))}
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
