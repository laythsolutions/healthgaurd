'use client';

import { MapPin } from 'lucide-react';
import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';
import { GradientText } from '@/components/animations';

export function InspectorSchedule() {
  const scheduledInspections = [
    { id: 1, restaurant: 'Downtown Bistro', address: '123 Main St', date: '2024-02-07', time: '10:00 AM', priority: 'high' },
    { id: 2, restaurant: 'Uptown Cafe', address: '456 Oak Ave', date: '2024-02-07', time: '2:00 PM', priority: 'normal' },
    { id: 3, restaurant: 'Midtown Diner', address: '789 Elm St', date: '2024-02-08', time: '9:00 AM', priority: 'normal' },
  ];

  return (
    <AnimatedPageWrapper animation="fade">
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Upcoming Inspections</CardTitle>
          <CardDescription>Your inspection queue</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {scheduledInspections.map((inspection) => (
              <div
                key={inspection.id}
                className="p-4 border rounded-lg card-lift bg-gradient-to-r from-background to-muted/20"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-lg">
                        <GradientText variant="warning">{inspection.restaurant}</GradientText>
                      </h3>
                      {inspection.priority === 'high' && (
                        <span className="status-badge status-badge-critical animate-pulse">PRIORITY</span>
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
                    <button className="px-4 py-2 bg-gradient-to-r from-orange-600 to-amber-600 text-white rounded-lg hover:shadow-lg hover:scale-105 transition-all duration-300 font-medium">
                      Start Inspection
                    </button>
                    <button className="px-4 py-2 border rounded-lg hover:bg-muted transition-all">
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
