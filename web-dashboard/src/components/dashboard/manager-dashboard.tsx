'use client';

import { useState } from 'react';
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
    complianceScore: 0,
    activeDevices: 0,
    pendingTasks: 0,
    staffOnDuty: 0,
    avgTemperature: 0,
    weeklyAlerts: 0
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-3xl font-bold">Manager Dashboard</h1>
                <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
                  MANAGER
                </span>
              </div>
              <p className="text-muted-foreground">Restaurant Operations</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                <Plus className="h-4 w-4 inline mr-2" />
                New Task
              </button>
              <button className="px-4 py-2 border rounded-lg hover:bg-muted">
                <FileText className="h-4 w-4 inline mr-2" />
                Generate Report
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Restaurant Stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.complianceScore.toFixed(1)}%</div>
              <p className="text-xs text-muted-foreground">Overall score</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Staff on Duty</CardTitle>
              <Users className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.staffOnDuty}</div>
              <p className="text-xs text-muted-foreground">{stats.pendingTasks} pending tasks</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Weekly Alerts</CardTitle>
              <AlertTriangle className="h-4 w-4 text-orange-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.weeklyAlerts}</div>
              <p className="text-xs text-muted-foreground">This week</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Avg Temperature</CardTitle>
              <Thermometer className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.avgTemperature.toFixed(1)}°F</div>
              <p className="text-xs text-muted-foreground">All sensors</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="sensors" className="space-y-4">
          <TabsList className="grid w-full grid-cols-6 lg:w-auto">
            <TabsTrigger value="sensors">Sensors</TabsTrigger>
            <TabsTrigger value="tasks">Tasks</TabsTrigger>
            <TabsTrigger value="staff">Staff</TabsTrigger>
            <TabsTrigger value="logs">Logs</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
          </TabsList>

          <TabsContent value="sensors" className="space-y-4">
            <DeviceManagement restaurantId={restaurantId} />
          </TabsContent>

          <TabsContent value="tasks" className="space-y-4">
            <Card>
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
                  ].map((task) => (
                    <div key={task.task} className="p-4 border rounded-lg flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${
                          task.status === 'complete' ? 'bg-green-500' :
                          task.status === 'in-progress' ? 'bg-yellow-500' :
                          'bg-gray-300'
                        }`} />
                        <div>
                          <p className="font-medium">{task.task}</p>
                          <p className="text-sm text-muted-foreground">
                            Assigned to {task.assigned} • {task.time}
                          </p>
                        </div>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded ${
                        task.status === 'complete' ? 'bg-green-100 text-green-700' :
                        task.status === 'in-progress' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {task.status}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="staff" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Staff Schedule</CardTitle>
                <CardDescription>Manage shifts and assignments</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
                    <div key={day} className="border rounded-lg p-4">
                      <p className="font-semibold mb-2">{day}</p>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full" />
                          <span>Maria S.</span>
                          <span className="text-muted-foreground text-xs">8AM-4PM</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full" />
                          <span>John D.</span>
                          <span className="text-muted-foreground text-xs">4PM-12AM</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="logs" className="space-y-4">
            <Card>
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
                  ].map((log) => (
                    <div key={log.time} className="p-4 border rounded-lg flex items-center justify-between">
                      <div>
                        <p className="font-medium">{log.type} Log</p>
                        <p className="text-sm text-muted-foreground">
                          {log.staff} • {log.time} • {log.value}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs px-2 py-1 rounded ${
                          log.status === 'approved' ? 'bg-green-100 text-green-700' :
                          'bg-yellow-100 text-yellow-700'
                        }`}>
                          {log.status}
                        </span>
                        {log.status === 'pending' && (
                          <button className="text-xs bg-primary text-primary-foreground px-2 py-1 rounded">
                            Review
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reports" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Compliance Reports</CardTitle>
                    <CardDescription>Generate and manage reports</CardDescription>
                  </div>
                  <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg">
                    <Plus className="h-4 w-4 inline mr-2" />
                    New Report
                  </button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  {[
                    { name: 'Daily Summary', frequency: 'Daily', lastRun: 'Today 6:00 AM' },
                    { name: 'Weekly Report', frequency: 'Weekly', lastRun: 'Monday 6:00 AM' },
                    { name: 'Monthly Report', frequency: 'Monthly', lastRun: 'Jan 1, 2024' },
                    { name: 'Inspection Prep', frequency: 'On-demand', lastRun: 'Dec 15, 2023' },
                  ].map((report) => (
                    <div key={report.name} className="border rounded-lg p-4">
                      <p className="font-semibold">{report.name}</p>
                      <p className="text-sm text-muted-foreground">{report.frequency}</p>
                      <p className="text-xs text-muted-foreground mt-2">Last: {report.lastRun}</p>
                      <button className="mt-3 text-xs bg-secondary px-3 py-1.5 rounded hover:bg-secondary/80">
                        Generate
                      </button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="alerts" className="space-y-4">
            <AlertsList restaurantId={restaurantId} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
