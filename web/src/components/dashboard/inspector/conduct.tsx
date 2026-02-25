'use client';

import { Search } from 'lucide-react';
import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { GlassCard } from '@/components/layout';
import { AnimatedPageWrapper } from '@/components/layout/animated-page-wrapper';

export function InspectorConduct() {
  return (
    <AnimatedPageWrapper animation="fade">
      <GlassCard variant="default">
        <CardHeader>
          <CardTitle>Conduct Inspection</CardTitle>
          <CardDescription>Complete a health inspection</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div>
              <label className="text-sm font-medium mb-2 block">Search Restaurant</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Enter restaurant name or address..."
                  className="flex-1 px-4 py-2 border rounded-lg bg-background/50 backdrop-blur focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500 transition-all"
                />
                <button className="px-4 py-2 bg-gradient-to-r from-orange-600 to-amber-600 text-white rounded-lg hover:shadow-md transition-all">
                  <Search className="h-4 w-4 inline mr-2" />
                  Search
                </button>
              </div>
            </div>

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
                  <div key={idx} className="flex items-center gap-3 p-3 border rounded-lg hover:bg-muted/50 transition-all card-lift">
                    <input type="checkbox" className="w-5 h-5 accent-orange-500" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-t pt-6">
              <label className="text-sm font-medium mb-2 block">Final Score (0-100)</label>
              <input
                type="number"
                min="0"
                max="100"
                placeholder="Enter score"
                className="w-full px-4 py-2 border rounded-lg bg-background/50 backdrop-blur focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500 transition-all"
              />
            </div>

            <div className="border-t pt-6">
              <label className="text-sm font-medium mb-2 block">Inspector Notes</label>
              <textarea
                rows={4}
                placeholder="Add notes about violations, observations, recommendations..."
                className="w-full px-4 py-2 border rounded-lg bg-background/50 backdrop-blur focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500 transition-all"
              />
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <button className="px-4 py-2 border rounded-lg hover:bg-muted transition-all">
                Save Draft
              </button>
              <button className="px-4 py-2 bg-gradient-to-r from-orange-600 to-amber-600 text-white rounded-lg hover:shadow-lg hover:scale-105 transition-all duration-300 font-medium">
                Submit Inspection
              </button>
            </div>
          </div>
        </CardContent>
      </GlassCard>
    </AnimatedPageWrapper>
  );
}
