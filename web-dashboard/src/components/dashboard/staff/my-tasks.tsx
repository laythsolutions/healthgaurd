'use client';

import { useState } from 'react';
import { CheckCircle, Clock } from 'lucide-react';
import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';

export function StaffMyTasks() {
  const [todayTasks, setTodayTasks] = useState([
    { id: 1, task: 'Morning temperature check', completed: true, dueTime: '8:00 AM' },
    { id: 2, task: 'Cold storage inspection', completed: false, dueTime: '10:00 AM' },
    { id: 3, task: 'Hot holding verification', completed: false, dueTime: '12:00 PM' },
    { id: 4, task: 'Cleaning log', completed: false, dueTime: '2:00 PM' },
    { id: 5, task: 'Closing procedures', completed: false, dueTime: '10:00 PM' },
  ]);

  const toggleTask = (id: number) => {
    setTodayTasks(tasks =>
      tasks.map(task =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  return (
    <AnimatedPageWrapper animation="fade">
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>My Tasks</CardTitle>
          <CardDescription>Complete your assigned tasks for today</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {todayTasks.map((task, index) => (
              <div
                key={task.id}
                className={`p-4 border rounded-lg flex items-center justify-between cursor-pointer transition-all duration-300 card-lift ${
                  task.completed
                    ? 'bg-gradient-to-r from-emerald-500/10 to-green-500/10 border-emerald-500/30 glow-emerald'
                    : 'hover:bg-muted/50'
                }`}
                onClick={() => toggleTask(task.id)}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-300 ${
                    task.completed
                      ? 'bg-gradient-to-r from-emerald-500 to-green-500 border-emerald-500 scale-110'
                      : 'border-gray-300'
                  }`}>
                    {task.completed && <CheckCircle className="h-4 w-4 text-white" />}
                  </div>
                  <div>
                    <p className={`font-medium ${task.completed ? 'line-through text-muted-foreground' : ''}`}>
                      {task.task}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      <Clock className="h-3 w-3 inline mr-1" />
                      Due: {task.dueTime}
                    </p>
                  </div>
                </div>
                {task.completed && (
                  <span className="status-badge status-badge-success">done</span>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
