'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Thermometer, Activity } from 'lucide-react';

interface SensorChartProps {
  restaurantId: string;
}

interface SensorReading {
  timestamp: string;
  temperature: number;
  device_name: string;
}

interface SensorDataPoint {
  time: string;
  temperature: number;
}

export function SensorChart({ restaurantId }: SensorChartProps) {
  const [readings, setReadings] = useState<SensorDataPoint[]>([]);
  const [currentTemp, setCurrentTemp] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Generate more realistic mock data for demo
    const generateData = () => {
      const now = Date.now();
      const data: SensorDataPoint[] = [];
      let temp = 38;

      for (let i = 24; i >= 0; i--) {
        const timestamp = new Date(now - i * 3600000); // Hourly intervals
        const time = timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

        // Simulate temperature fluctuations
        const fluctuation = (Math.random() - 0.5) * 2; // ±1 degree
        temp = Math.max(35, Math.min(42, temp + fluctuation));

        data.push({ time, temperature: parseFloat(temp.toFixed(1)) });
      }

      setCurrentTemp(data[data.length - 1].temperature);
      setReadings(data);
      setIsLoading(false);
    };

    generateData();

    // Refresh every 5 minutes
    const interval = setInterval(() => {
      const lastTemp = readings[readings.length - 1]?.temperature || 38;
      const newTemp = lastTemp + (Math.random() - 0.5) * 1;
      const newPoint = {
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        temperature: parseFloat(newTemp.toFixed(1))
      };

      setCurrentTemp(newPoint.temperature);
      setReadings(prev => [...prev.slice(1), newPoint]);
    }, 300000); // 5 minutes

    return () => clearInterval(interval);
  }, [restaurantId]);

  const getTemperatureStatus = (temp: number) => {
    if (temp < 33) return { status: 'critical', color: 'text-red-600', label: 'Too Cold' };
    if (temp > 41) return { status: 'critical', color: 'text-red-600', label: 'Too Hot' };
    if (temp < 35) return { status: 'warning', color: 'text-yellow-600', label: 'Low' };
    if (temp > 39) return { status: 'warning', color: 'text-yellow-600', label: 'Elevated' };
    return { status: 'safe', color: 'text-green-600', label: 'Normal' };
  };

  const status = getTemperatureStatus(currentTemp);

  if (isLoading) {
    return (
    <div className="h-[300px] flex items-center justify-center border rounded-lg bg-muted/20">
      <div className="text-center">
        <Activity className="h-8 w-8 mx-auto mb-2 animate-pulse" />
        <p className="text-muted-foreground">Loading sensor data...</p>
      </div>
    </div>
  );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Temperature Monitoring</CardTitle>
        <CardDescription>Real-time temperature readings from all sensors</CardDescription>
      </CardHeader>
      <CardContent>
        {/* Current Temperature Display */}
        <div className="mb-6 p-6 border rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Current Temperature</p>
              <div className="flex items-baseline gap-2">
                <span className="text-5xl font-bold">{currentTemp.toFixed(1)}</span>
                <span className="text-2xl text-muted-foreground">°F</span>
              </div>
              <p className={`text-sm font-semibold mt-1 ${status.color}`}>
                {status.label}
              </p>
            </div>
            <Thermometer className={`h-12 w-12 ${
              status.status === 'safe' ? 'text-green-500' :
              status.status === 'warning' ? 'text-yellow-500' :
              'text-red-500'
            }`} />
          </div>
        </div>

        {/* Chart */}
        <div className="h-[250px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={readings}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="time"
                stroke="#6b7280"
                style={{ fontSize: 12 }}
              />
              <YAxis
                domain={[30, 45]}
                stroke="#6b7280"
                style={{ fontSize: 12 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  border: 'none',
                  borderRadius: '4px',
                  color: '#fff',
                }}
                labelFormatter={(value) => `${value}°F`}
              />
              <Line
                type="monotone"
                dataKey="temperature"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
                isAnimationActive={false}
              />
              <Legend />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Safe Range Indicator */}
        <div className="mt-4 flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Safe range:</span>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span>33°F - 41°F</span>
            </div>
            <div className="flex items-center gap-1">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Updates every 5 min</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
