'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';

interface SensorChartProps {
  restaurantId: string;
}

interface SensorReading {
  timestamp: string;
  temperature: number;
  device_name: string;
}

export function SensorChart({ restaurantId }: SensorChartProps) {
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Mock data for now
    const mockData: SensorReading[] = Array.from({ length: 24 }, (_, i) => ({
      timestamp: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
      temperature: 35 + Math.random() * 10,
      device_name: 'Sensor 1',
    }));
    setReadings(mockData);
    setIsLoading(false);
  }, [restaurantId]);

  if (isLoading) {
    return <div className="text-muted-foreground">Loading chart...</div>;
  }

  return (
    <div className="h-[300px] flex items-center justify-center border rounded-lg bg-muted/20">
      <div className="text-center">
        <p className="text-4xl font-bold text-primary mb-2">
          {readings[readings.length - 1]?.temperature.toFixed(1)}°F
        </p>
        <p className="text-sm text-muted-foreground">Current Temperature</p>
        <p className="text-xs text-muted-foreground mt-4">
          Chart visualization coming soon
        </p>
      </div>
    </div>
  );
}
