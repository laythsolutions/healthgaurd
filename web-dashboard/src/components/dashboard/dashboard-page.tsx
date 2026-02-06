'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Activity, AlertTriangle, CheckCircle, Thermometer, Wifi, WifiOff } from 'lucide-react';
import { SensorChart } from '@/components/sensors/sensor-chart';
import { AlertsList } from '@/components/alerts/alerts-list';
import { RestaurantSelect } from '@/components/restaurants/restaurant-select';
import { useDashboardData } from '@/hooks/use-dashboard-data';

export function DashboardPage() {
  const [selectedRestaurant, setSelectedRestaurant] = useState<string>('');
  const { data, isLoading, error } = useDashboardData(selectedRestaurant);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">HealthGuard</h1>
              <p className="text-muted-foreground">Restaurant Compliance Monitoring</p>
            </div>
            <div className="flex items-center gap-4">
              <RestaurantSelect
                value={selectedRestaurant}
                onChange={setSelectedRestaurant}
              />
              <div className="flex items-center gap-2 text-sm">
                <Wifi className="h-4 w-4 text-green-500" />
                <span>Connected</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-muted-foreground">Loading dashboard...</div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-destructive">Error loading dashboard</div>
          </div>
        ) : (
          <>
            {/* Summary Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
                  <CheckCircle className="h-4 w-4 text-green-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {data?.summary?.compliance_score?.toFixed(1) || '0.0'}%
                  </div>
                  <p className="text-xs text-muted-foreground">Overall compliance</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Devices</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {data?.summary?.active_devices || 0}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {data?.summary?.offline_devices || 0} offline
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Critical Alerts</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-destructive" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {data?.summary?.critical_alerts || 0}
                  </div>
                  <p className="text-xs text-muted-foreground">Need attention</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Avg Temperature</CardTitle>
                  <Thermometer className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {data?.summary?.avg_temperature?.toFixed(1) || '--'}°F
                  </div>
                  <p className="text-xs text-muted-foreground">Across all sensors</p>
                </CardContent>
              </Card>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="sensors" className="space-y-4">
              <TabsList>
                <TabsTrigger value="sensors">Sensors</TabsTrigger>
                <TabsTrigger value="alerts">Alerts</TabsTrigger>
                <TabsTrigger value="logs">Logs</TabsTrigger>
                <TabsTrigger value="reports">Reports</TabsTrigger>
              </TabsList>

              <TabsContent value="sensors" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Temperature Readings</CardTitle>
                    <CardDescription>Real-time sensor data from your restaurant</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <SensorChart restaurantId={selectedRestaurant} />
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="alerts" className="space-y-4">
                <AlertsList restaurantId={selectedRestaurant} />
              </TabsContent>

              <TabsContent value="logs" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Manual Logs</CardTitle>
                    <CardDescription>Temperature and compliance logs</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">Manual logs feature coming soon...</p>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="reports" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Compliance Reports</CardTitle>
                    <CardDescription>Generate and download compliance reports</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">Reports feature coming soon...</p>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </>
        )}
      </main>
    </div>
  );
}
