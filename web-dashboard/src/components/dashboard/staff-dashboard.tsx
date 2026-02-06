'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Thermometer,
  CheckCircle,
  Clock,
  ListChecks,
  Bell,
  LogOut
} from 'lucide-react';

/**
 * STAFF DASHBOARD
 *
 * Features:
 * - Simplified, task-focused interface
 * - Today's checklist
 * - Quick temperature logging
 * - My task assignments
 * - Training materials
 * - Mobile-optimized
 */
export function StaffDashboard({ restaurantId, staffName }: { restaurantId: string, staffName: string }) {
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

  const completedCount = todayTasks.filter(t => t.completed).length;
  const progressPercent = (completedCount / todayTasks.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/20 pb-20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">My Dashboard</h1>
              <p className="text-muted-foreground">Welcome back, {staffName}!</p>
            </div>
            <button className="text-sm text-muted-foreground flex items-center gap-2">
              <LogOut className="h-4 w-4" />
              Clock Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Progress Card */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Today's Progress</CardTitle>
                <CardDescription>{completedCount} of {todayTasks.length} tasks completed</CardDescription>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold">{progressPercent.toFixed(0)}%</div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-green-500 h-3 rounded-full transition-all"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid gap-4 md:grid-cols-2 mb-6">
          <Card className="border-2 border-dashed cursor-pointer hover:border-primary">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <Thermometer className="h-8 w-8 text-blue-500" />
                <div>
                  <p className="font-semibold">Log Temperature</p>
                  <p className="text-sm text-muted-foreground">Quick entry</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-dashed cursor-pointer hover:border-primary">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <ListChecks className="h-8 w-8 text-green-500" />
                <div>
                  <p className="font-semibold">View Checklist</p>
                  <p className="text-sm text-muted-foreground">All tasks</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="tasks" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="tasks">Tasks</TabsTrigger>
            <TabsTrigger value="sensors">Sensors</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
            <TabsTrigger value="training">Training</TabsTrigger>
          </TabsList>

          <TabsContent value="tasks" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>My Tasks</CardTitle>
                <CardDescription>Complete your assigned tasks for today</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {todayTasks.map((task) => (
                    <div
                      key={task.id}
                      className={`p-4 border rounded-lg flex items-center justify-between cursor-pointer transition-colors ${
                        task.completed ? 'bg-green-50 border-green-200' : 'hover:bg-muted/50'
                      }`}
                      onClick={() => toggleTask(task.id)}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                          task.completed ? 'bg-green-500 border-green-500' : 'border-gray-300'
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
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sensors" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Quick Temperature Check</CardTitle>
                <CardDescription>Verify sensor readings</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { sensor: 'Walk-in Cooler', current: '36°F', status: 'ok' },
                    { sensor: 'Walk-in Freezer', current: '-2°F', status: 'ok' },
                    { sensor: 'Hot Holding', current: '145°F', status: 'warning' },
                    { sensor: 'Cold Holding', current: '38°F', status: 'ok' },
                  ].map((sensor) => (
                    <div key={sensor.sensor} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <p className="font-medium">{sensor.sensor}</p>
                        <p className="text-2xl font-bold">{sensor.current}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm ${
                        sensor.status === 'ok' ? 'bg-green-100 text-green-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {sensor.status === 'ok' ? '✓ Normal' : '⚠ Check'}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="alerts" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Alerts</CardTitle>
                <CardDescription>Notifications relevant to you</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg">
                    <p className="font-semibold text-yellow-900">⚠ Hot Holding Temperature</p>
                    <p className="text-sm text-yellow-700">Hot holding is at 145°F (should be above 135°F)</p>
                    <p className="text-xs text-muted-foreground mt-2">5 minutes ago</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="training" className="space-y-4">
            <Card>
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
                    <div key={training.title} className="p-4 border rounded-lg flex items-center justify-between">
                      <div>
                        <p className="font-medium">{training.title}</p>
                        <p className="text-sm text-muted-foreground">
                          <Clock className="h-3 w-3 inline mr-1" />
                          {training.duration}
                        </p>
                      </div>
                      <button className={`text-sm px-3 py-1 rounded ${
                        training.completed ? 'bg-green-100 text-green-700' : 'bg-primary text-primary-foreground'
                      }`}>
                        {training.completed ? '✓ Completed' : 'Start'}
                      </button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
