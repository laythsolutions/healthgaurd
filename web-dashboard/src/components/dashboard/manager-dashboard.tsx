'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Thermometer,
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText,
  Plus,
  Calendar,
  TrendingUp,
  Users
} from 'lucide-react';
import { SensorChartViz as SensorChart } from '@/components/sensors/sensor-chart-viz';
import { AlertsList } from '@/components/alerts/alerts-list';
import { DeviceManagement } from '@/components/devices';
import { AnimatedBackground, GlassCard } from '@/components/layout';
import { KPICard } from './kpi-card';
import { AnimatedPageWrapper, StaggeredGrid } from '@/components/layout/animated-page-wrapper';
import { GradientText } from '@/components/animations';

/**
 * MANAGER DASHBOARD
 *
 * Features:
 * - Single restaurant comprehensive view
 * - Staff scheduling and task assignment
 * - Compliance reporting
 * - Manual log review and approval
 * - Alert management
 * - Performance analytics
 */
export function ManagerDashboard({ restaurantId }: { restaurantId: string }) {
  const [stats, setStats] = useState({
    complianceScore: 94.5,
    activeDevices: 24,
    pendingTasks: 7,
    staffOnDuty: 5,
    avgTemperature: 38.2,
    weeklyAlerts: 3
  });

  useEffect(() => {
    // Simulate data updates
    const interval = setInterval(() => {
      setStats(prev => ({
        ...prev,
        avgTemperature: 35 + Math.random() * 10,
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen relative">
      {/* Animated Background */}
      <AnimatedBackground variant="gradient" intensity="medium" />

      {/* Header */}
      <header className="border-b glass-dark sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-3xl font-bold">
                  <GradientText variant="primary">Manager Dashboard</GradientText>
                </h1>
                <span className="px-3 py-1 text-xs bg-gradient-to-r from-violet-500 to-indigo-500 text-white rounded-full font-semibold shadow-lg">
                  MANAGER
                </span>
              </div>
              <p className="text-muted-foreground">Restaurant Operations</p>
            </div>
            <div className="flex items-center gap-3">
              <button className="px-4 py-2 bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-lg hover:shadow-lg hover:scale-105 transition-all duration-300 font-medium">
                <Plus className="h-4 w-4 inline mr-2" />
                New Task
              </button>
              <button className="px-4 py-2 border border-border rounded-lg hover:bg-muted hover:shadow-md transition-all duration-300 font-medium">
                <FileText className="h-4 w-4 inline mr-2" />
                Generate Report
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 relative z-10">
        {/* Restaurant Stats */}
        <AnimatedPageWrapper animation="stagger" staggerAmount={0.1} delay={0.2}>
          <StaggeredGrid cols={4} className="mb-8">
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

        {/* Tabs */}
        <Tabs defaultValue="sensors" className="space-y-4">
          <TabsList className="grid w-full grid-cols-6 lg:w-auto glass-dark p-1">
            <TabsTrigger value="sensors" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-violet-600 data-[state=active]:to-indigo-600">Sensors</TabsTrigger>
            <TabsTrigger value="tasks" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-violet-600 data-[state=active]:to-indigo-600">Tasks</TabsTrigger>
            <TabsTrigger value="staff" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-violet-600 data-[state=active]:to-indigo-600">Staff</TabsTrigger>
            <TabsTrigger value="logs" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-violet-600 data-[state=active]:to-indigo-600">Logs</TabsTrigger>
            <TabsTrigger value="reports" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-violet-600 data-[state=active]:to-indigo-600">Reports</TabsTrigger>
            <TabsTrigger value="alerts" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-violet-600 data-[state=active]:to-indigo-600">Alerts</TabsTrigger>
          </TabsList>

          <TabsContent value="sensors" className="space-y-4">
            <DeviceManagement restaurantId={restaurantId} />
          </TabsContent>

          <TabsContent value="tasks" className="space-y-4">
            <AnimatedPageWrapper animation="fade">
              <GlassCard variant="default">
                <CardHeader>
                  <CardTitle>Today's Tasks</CardTitle>
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
                              Assigned to {task.assigned} • {task.time}
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
          </TabsContent>

          <TabsContent value="staff" className="space-y-4">
            <AnimatedPageWrapper animation="stagger" staggerAmount={0.1}>
              <GlassCard variant="default">
                <CardHeader>
                  <CardTitle>Staff Schedule</CardTitle>
                  <CardDescription>Manage shifts and assignments</CardDescription>
                </CardHeader>
                <CardContent>
                  <StaggeredGrid cols={3}>
                    {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
                      <div key={day} className="border rounded-lg p-4 card-lift bg-gradient-to-br from-background to-muted/30">
                        <p className="font-semibold mb-3 text-lg">{day}</p>
                        <div className="space-y-2 text-sm">
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-emerald-500 rounded-full glow-emerald" />
                            <span>Maria S.</span>
                            <span className="text-muted-foreground text-xs">8AM-4PM</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-blue-500 rounded-full glow-cyan" />
                            <span>John D.</span>
                            <span className="text-muted-foreground text-xs">4PM-12AM</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </StaggeredGrid>
                </CardContent>
              </GlassCard>
            </AnimatedPageWrapper>
          </TabsContent>

          <TabsContent value="logs" className="space-y-4">
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
                        key={log.time}
                        className="p-4 border rounded-lg flex items-center justify-between card-lift bg-gradient-to-r from-background to-muted/20 stagger-item"
                        style={{ animationDelay: `${index * 0.15}s` }}
                      >
                        <div>
                          <p className="font-medium">{log.type} Log</p>
                          <p className="text-sm text-muted-foreground">
                            {log.staff} • {log.time} • {log.value}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`status-badge ${
                            log.status === 'approved' ? 'status-badge-success' : 'status-badge-warning'
                          }`}>
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
          </TabsContent>

          <TabsContent value="reports" className="space-y-4">
            <AnimatedPageWrapper animation="stagger" staggerAmount={0.1}>
              <GlassCard variant="default">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Compliance Reports</CardTitle>
                      <CardDescription>Generate and manage reports</CardDescription>
                    </div>
                    <button className="px-4 py-2 bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-lg hover:shadow-lg transition-all">
                      <Plus className="h-4 w-4 inline mr-2" />
                      New Report
                    </button>
                  </div>
                </CardHeader>
                <CardContent>
                  <StaggeredGrid cols={2}>
                    {[
                      { name: 'Daily Summary', frequency: 'Daily', lastRun: 'Today 6:00 AM' },
                      { name: 'Weekly Report', frequency: 'Weekly', lastRun: 'Monday 6:00 AM' },
                      { name: 'Monthly Report', frequency: 'Monthly', lastRun: 'Jan 1, 2024' },
                      { name: 'Inspection Prep', frequency: 'On-demand', lastRun: 'Dec 15, 2023' },
                    ].map((report) => (
                      <div key={report.name} className="border rounded-lg p-4 card-lift bg-gradient-to-br from-background to-muted/30">
                        <p className="font-semibold">{report.name}</p>
                        <p className="text-sm text-muted-foreground">{report.frequency}</p>
                        <p className="text-xs text-muted-foreground mt-2">Last: {report.lastRun}</p>
                        <button className="mt-3 text-xs bg-secondary px-3 py-1.5 rounded hover:bg-secondary/80 transition-all">
                          Generate
                        </button>
                      </div>
                    ))}
                  </StaggeredGrid>
                </CardContent>
              </GlassCard>
            </AnimatedPageWrapper>
          </TabsContent>

          <TabsContent value="alerts" className="space-y-4">
            <AlertsList restaurantId={restaurantId} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
