'use client';

import { useEffect, useState, useRef } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useGSAP } from '@/hooks/use-gsap';

interface SensorChartProps {
  restaurantId: string;
  timeRange?: '24h' | '7d' | '30d' | '90d';
}

interface SensorReading {
  timestamp: string;
  temperature: number;
  humidity?: number;
}

export function SensorChartEnhanced({ restaurantId, timeRange = '24h' }: SensorChartProps) {
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentValue, setCurrentValue] = useState<number>(0);
  const chartRef = useRef<HTMLDivElement>(null);

  // Animate chart entrance
  useGSAP(() => {
    if (chartRef.current && !isLoading) {
      window.gsap.fromTo(
        chartRef.current,
        { opacity: 0, scale: 0.95 },
        { opacity: 1, scale: 1, duration: 0.6, ease: 'power2.out' }
      );
    }
  }, [isLoading]);

  useEffect(() => {
    // Generate mock data based on time range
    const generateData = () => {
      const now = new Date();
      const points = timeRange === '24h' ? 24 : timeRange === '7d' ? 7 : 30;
      const interval = timeRange === '24h' ? 3600000 : 86400000; // 1 hour or 1 day

      const data: SensorReading[] = Array.from({ length: points }, (_, i) => {
        const timestamp = new Date(now.getTime() - (points - 1 - i) * interval);
        // Simulate realistic temperature with day/night variation
        const baseTemp = 38;
        const variation = Math.sin((i / points) * Math.PI * 2) * 5;
        const random = (Math.random() - 0.5) * 2;
        const temperature = baseTemp + variation + random;

        return {
          timestamp: timestamp.toISOString(),
          temperature: Math.round(temperature * 10) / 10,
        };
      });

      setReadings(data);
      setCurrentValue(data[data.length - 1].temperature);
      setIsLoading(false);
    };

    const timer = setTimeout(generateData, 300);
    return () => clearTimeout(timer);
  }, [restaurantId, timeRange]);

  // Format timestamp for display
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    if (timeRange === '24h') {
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Temperature status
  const getTempStatus = (temp: number) => {
    if (temp > 45) return { status: 'critical', color: '#ef4444', label: 'Too Hot' };
    if (temp < 32) return { status: 'critical', color: '#3b82f6', label: 'Too Cold' };
    if (temp > 42) return { status: 'warning', color: '#f59e0b', label: 'Warm' };
    if (temp < 35) return { status: 'warning', color: '#f59e0b', label: 'Cool' };
    return { status: 'good', color: '#10b981', label: 'Optimal' };
  };

  const tempStatus = getTempStatus(currentValue);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-[300px]">
          <div className="text-center">
            <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-sm text-muted-foreground">Loading sensor data...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div ref={chartRef} className="space-y-4">
      {/* Current Value Card */}
      <Card className="bg-gradient-to-br from-background to-muted/20">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Current Temperature</CardTitle>
              <CardDescription>Real-time sensor readings</CardDescription>
            </div>
            <div
              className="px-3 py-1 rounded-full text-xs font-medium"
              style={{
                backgroundColor: `${tempStatus.color}20`,
                color: tempStatus.color,
              }}
            >
              {tempStatus.label}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-end gap-4">
            <div>
              <div className="text-5xl font-bold tabular-nums">
                {currentValue.toFixed(1)}°F
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Safe range: 35°F - 42°F
              </p>
            </div>
            <div className="flex-1">
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${((currentValue - 30) / 30) * 100}%`,
                    backgroundColor: tempStatus.color,
                  }}
                />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>30°F</span>
                <span>60°F</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Temperature Trend</CardTitle>
          <CardDescription>
            {timeRange === '24h' ? 'Last 24 hours' : timeRange === '7d' ? 'Last 7 days' : 'Last 30 days'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={readings}>
              <defs>
                <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={tempStatus.color} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={tempStatus.color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={formatTime}
                stroke="#6b7280"
                fontSize={12}
              />
              <YAxis
                domain={[30, 50]}
                stroke="#6b7280"
                fontSize={12}
                label={{ value: 'Temperature (°F)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
                labelFormatter={formatTime}
                formatter={(value: number) => [`${value.toFixed(1)}°F`, 'Temperature']}
              />
              <Area
                type="monotone"
                dataKey="temperature"
                stroke={tempStatus.color}
                strokeWidth={2}
                fill="url(#tempGradient)"
                animationDuration={1000}
                animationBegin={300}
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
