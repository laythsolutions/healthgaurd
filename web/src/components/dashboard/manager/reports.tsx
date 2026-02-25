'use client';

import { Plus } from 'lucide-react';
import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper, StaggeredGrid } from '@/components/layout/animated-page-wrapper';

export function ManagerReports() {
  return (
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
  );
}
