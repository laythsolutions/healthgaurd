'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Building2,
  Users,
  TrendingUp,
  AlertTriangle,
  DollarSign,
  MapPin,
  BarChart3,
  Settings,
  Plus
} from 'lucide-react';

/**
 * ADMIN DASHBOARD
 *
 * Features:
 * - Multi-restaurant/organization oversight
 * - Aggregate analytics across all locations
 * - User and team management
 * - Billing and subscription management
 * - System-wide alerts
 * - Performance benchmarking
 */
export function AdminDashboard() {
  const [stats, setStats] = useState({
    totalRestaurants: 0,
    totalUsers: 0,
    avgComplianceScore: 0,
    monthlyRevenue: 0,
    activeAlerts: 0,
    systemHealth: 'operational'
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-3xl font-bold">Admin Dashboard</h1>
                <span className="px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded-full">
                  ADMIN
                </span>
              </div>
              <p className="text-muted-foreground">Organization Overview</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                <Plus className="h-4 w-4 inline mr-2" />
                Add Restaurant
              </button>
              <Settings className="h-6 w-6 text-muted-foreground cursor-pointer hover:text-foreground" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Organization Stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Restaurants</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalRestaurants}</div>
              <p className="text-xs text-muted-foreground">Across all regions</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalUsers}</div>
              <p className="text-xs text-muted-foreground">Active team members</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Avg Compliance</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.avgComplianceScore.toFixed(1)}%</div>
              <p className="text-xs text-muted-foreground">Organization-wide</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.monthlyRevenue.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">Recurring MRR</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="restaurants" className="space-y-4">
          <TabsList className="grid w-full grid-cols-6 lg:w-auto">
            <TabsTrigger value="restaurants">Restaurants</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="alerts">System Alerts</TabsTrigger>
            <TabsTrigger value="billing">Billing</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="restaurants" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Restaurant Portfolio</CardTitle>
                <CardDescription>Manage all restaurants in your organization</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Restaurant list with performance metrics */}
                  <div className="border rounded-lg divide-y">
                    {[
                      { name: 'Downtown Location', score: 94.5, status: 'excellent', alerts: 0 },
                      { name: 'Midtown Branch', score: 88.2, status: 'good', alerts: 2 },
                      { name: 'Uptown Bistro', score: 76.8, status: 'attention', alerts: 5 },
                      { name: 'Suburban Cafe', score: 91.3, status: 'good', alerts: 1 },
                    ].map((restaurant) => (
                      <div key={restaurant.name} className="p-4 flex items-center justify-between hover:bg-muted/50">
                        <div className="flex-1">
                          <p className="font-medium">{restaurant.name}</p>
                          <p className="text-sm text-muted-foreground">
                            Compliance: <span className={`font-semibold ${
                              restaurant.score >= 90 ? 'text-green-600' :
                              restaurant.score >= 80 ? 'text-yellow-600' :
                              'text-red-600'
                            }`}>{restaurant.score}%</span>
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm">{restaurant.alerts} alerts</p>
                          <p className="text-xs text-muted-foreground">{restaurant.status}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="users" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>User Management</CardTitle>
                <CardDescription>Manage team members and permissions</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">User management interface...</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Organization Analytics</CardTitle>
                <CardDescription>Performance trends and insights</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Analytics charts...</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="alerts" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>System Alerts</CardTitle>
                <CardDescription>Critical issues across all locations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-4 border border-red-200 bg-red-50 rounded-lg flex items-start gap-3">
                    <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div>
                      <p className="font-semibold text-red-900">Critical: Uptown Bistro</p>
                      <p className="text-sm text-red-700">Temperature sensor offline for 2+ hours</p>
                    </div>
                  </div>
                  <div className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg flex items-start gap-3">
                    <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                    <div>
                      <p className="font-semibold text-yellow-900">Warning: Midtown Branch</p>
                      <p className="text-sm text-yellow-700">Compliance score dropped below 85%</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="billing" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Billing & Subscriptions</CardTitle>
                <CardDescription>Manage payment methods and invoices</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Billing interface...</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Organization Settings</CardTitle>
                <CardDescription>Configure organization-wide settings</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Settings interface...</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
