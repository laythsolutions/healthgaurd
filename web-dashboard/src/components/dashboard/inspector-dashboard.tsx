'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  ClipboardCheck,
  FileText,
  AlertTriangle,
  TrendingDown,
  Calendar,
  Search,
  MapPin
} from 'lucide-react';

/**
 * INSPECTOR DASHBOARD
 *
 * Features:
 * - Inspection routing and scheduling
 * - Restaurant queue management
 * - Violation tracking
 * - Compliance scorecards
 * - Follow-up scheduling
 * - Historical inspection data
 */
export function InspectorDashboard() {
  const [scheduledInspections, setScheduledInspections] = useState([
    { id: 1, restaurant: 'Downtown Bistro', address: '123 Main St', date: '2024-02-07', time: '10:00 AM', priority: 'high' },
    { id: 2, restaurant: 'Uptown Cafe', address: '456 Oak Ave', date: '2024-02-07', time: '2:00 PM', priority: 'normal' },
    { id: 3, restaurant: 'Midtown Diner', address: '789 Elm St', date: '2024-02-08', time: '9:00 AM', priority: 'normal' },
  ]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-3xl font-bold">Inspector Dashboard</h1>
                <span className="px-2 py-1 text-xs bg-orange-100 text-orange-700 rounded-full">
                  INSPECTOR
                </span>
              </div>
              <p className="text-muted-foreground">Health Inspection Management</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                <Calendar className="h-4 w-4 inline mr-2" />
                My Schedule
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Inspector Stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Today's Inspections</CardTitle>
              <ClipboardCheck className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{scheduledInspections.length}</div>
              <p className="text-xs text-muted-foreground">Scheduled</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Completed This Week</CardTitle>
              <FileText className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">24</div>
              <p className="text-xs text-muted-foreground">Inspections</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Critical Violations</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">3</div>
              <p className="text-xs text-muted-foreground">This week</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Avg Score Given</CardTitle>
              <TrendingDown className="h-4 w-4 text-yellow-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">87.3</div>
              <p className="text-xs text-muted-foreground">This month</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="scheduled" className="space-y-4">
          <TabsList className="grid w-full grid-cols-5 lg:w-auto">
            <TabsTrigger value="scheduled">Scheduled</TabsTrigger>
            <TabsTrigger value="conduct">Conduct Inspection</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
            <TabsTrigger value="violations">Violations</TabsTrigger>
            <TabsTrigger value="followups">Follow-ups</TabsTrigger>
          </TabsList>

          <TabsContent value="scheduled" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Inspections</CardTitle>
                <CardDescription>Your inspection queue</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {scheduledInspections.map((inspection) => (
                    <div key={inspection.id} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold text-lg">{inspection.restaurant}</h3>
                            {inspection.priority === 'high' && (
                              <span className="px-2 py-0.5 text-xs bg-red-100 text-red-700 rounded">
                                PRIORITY
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {inspection.address}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="text-sm">
                            <p className="text-muted-foreground">Date</p>
                            <p className="font-medium">{inspection.date}</p>
                          </div>
                          <div className="text-sm">
                            <p className="text-muted-foreground">Time</p>
                            <p className="font-medium">{inspection.time}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                            Start Inspection
                          </button>
                          <button className="px-4 py-2 border rounded-lg hover:bg-muted">
                            View Details
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="conduct" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Conduct Inspection</CardTitle>
                <CardDescription>Complete a health inspection</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Restaurant Search */}
                  <div>
                    <label className="text-sm font-medium mb-2 block">Search Restaurant</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="Enter restaurant name or address..."
                        className="flex-1 px-4 py-2 border rounded-lg"
                      />
                      <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg">
                        <Search className="h-4 w-4 inline mr-2" />
                        Search
                      </button>
                    </div>
                  </div>

                  {/* Inspection Form */}
                  <div className="border-t pt-6">
                    <h3 className="font-semibold mb-4">Inspection Checklist</h3>
                    <div className="space-y-3">
                      {[
                        'Food temperature control',
                        'Employee hygiene practices',
                        'Food storage and labeling',
                        'Equipment cleanliness',
                        'Pest control measures',
                        'Facility maintenance',
                        'Toxic substances labeling',
                        'Cross-contamination prevention',
                      ].map((item, idx) => (
                        <div key={idx} className="flex items-center gap-3 p-3 border rounded-lg">
                          <input type="checkbox" className="w-5 h-5" />
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Score Input */}
                  <div className="border-t pt-6">
                    <label className="text-sm font-medium mb-2 block">Final Score (0-100)</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      placeholder="Enter score"
                      className="w-full px-4 py-2 border rounded-lg"
                    />
                  </div>

                  {/* Notes */}
                  <div className="border-t pt-6">
                    <label className="text-sm font-medium mb-2 block">Inspector Notes</label>
                    <textarea
                      rows={4}
                      placeholder="Add notes about violations, observations, recommendations..."
                      className="w-full px-4 py-2 border rounded-lg"
                    />
                  </div>

                  <div className="flex justify-end gap-2 pt-4">
                    <button className="px-4 py-2 border rounded-lg hover:bg-muted">
                      Save Draft
                    </button>
                    <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                      Submit Inspection
                    </button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Inspection History</CardTitle>
                <CardDescription>Your past inspections</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { restaurant: 'Midtown Diner', date: '2024-02-05', score: 92, violations: 1 },
                    { restaurant: 'Downtown Bistro', date: '2024-02-03', score: 88, violations: 3 },
                    { restaurant: 'Uptown Cafe', date: '2024-02-01', score: 95, violations: 0 },
                    { restaurant: 'Suburban Grill', date: '2024-01-30', score: 76, violations: 5 },
                  ].map((inspection, idx) => (
                    <div key={idx} className="p-4 border rounded-lg flex items-center justify-between">
                      <div className="flex-1">
                        <p className="font-medium">{inspection.restaurant}</p>
                        <p className="text-sm text-muted-foreground">{inspection.date}</p>
                      </div>
                      <div className="text-right">
                        <p className={`text-2xl font-bold ${
                          inspection.score >= 90 ? 'text-green-600' :
                          inspection.score >= 80 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {inspection.score}
                        </p>
                        <p className="text-xs text-muted-foreground">{inspection.violations} violations</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="violations" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Violation Tracking</CardTitle>
                <CardDescription>Track and follow up on violations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { restaurant: 'Suburban Grill', violation: 'Cold holding at 45°F', date: '2024-01-30', status: 'pending' },
                    { restaurant: 'Downtown Bistro', violation: 'No hot water', date: '2024-02-03', status: 'resolved' },
                    { restaurant: 'Midtown Diner', violation: 'Improper sanitizing', date: '2024-02-05', status: 'pending' },
                  ].map((v, idx) => (
                    <div key={idx} className="p-4 border rounded-lg flex items-center justify-between">
                      <div className="flex-1">
                        <p className="font-medium">{v.restaurant}</p>
                        <p className="text-sm text-muted-foreground">{v.violation}</p>
                        <p className="text-xs text-muted-foreground">{v.date}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs ${
                        v.status === 'resolved' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {v.status}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="followups" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Scheduled Follow-ups</CardTitle>
                <CardDescription>Re-inspections for critical violations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { restaurant: 'Suburban Grill', violation: 'Cold holding', followupDate: '2024-02-10', daysRemaining: 3 },
                    { restaurant: 'Midtown Diner', violation: 'Sanitizing', followupDate: '2024-02-12', daysRemaining: 5 },
                  ].map((followup, idx) => (
                    <div key={idx} className="p-4 border border-orange-200 bg-orange-50 rounded-lg">
                      <p className="font-semibold">{followup.restaurant}</p>
                      <p className="text-sm text-muted-foreground">Violation: {followup.violation}</p>
                      <p className="text-sm text-muted-foreground">
                        Follow-up: {followup.followupDate} ({followup.daysRemaining} days)
                      </p>
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
