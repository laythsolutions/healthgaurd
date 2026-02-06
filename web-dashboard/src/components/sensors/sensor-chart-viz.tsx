'use client';

import { useEffect, useState, useRef } from 'react';
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
import { GlassCard } from '@/components/layout/glass-card';
import { CounterValue, GradientText, FloatingElement } from '@/components/animations';

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
  const chartRef = useRef<HTMLDivElement>(null);

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
    if (temp < 33) return { status: 'critical', color: 'text-rose-600', bgGradient: 'from-rose-500/10 to-red-500/10', label: 'Too Cold' };
    if (temp > 41) return { status: 'critical', color: 'text-rose-600', bgGradient: 'from-rose-500/10 to-red-500/10', label: 'Too Hot' };
    if (temp < 35) return { status: 'warning', color: 'text-amber-600', bgGradient: 'from-amber-500/10 to-orange-500/10', label: 'Low' };
    if (temp > 39) return { status: 'warning', color: 'text-amber-600', bgGradient: 'from-amber-500/10 to-orange-500/10', label: 'Elevated' };
    return { status: 'safe', color: 'text-emerald-600', bgGradient: 'from-emerald-500/10 to-green-500/10', label: 'Normal' };
  };

  const status = getTemperatureStatus(currentTemp);

  if (isLoading) {
    return (
    <div className="h-[300px] flex items-center justify-center border rounded-lg glass-card">
      <div className="text-center">
        <FloatingElement intensity="subtle">
          <Activity className="h-12 w-12 mx-auto mb-3 text-violet-500 animate-pulse" />
        </FloatingElement>
        <p className="text-muted-foreground">Loading sensor data...</p>
      </div>
    </div>
  );
  }

  return (
    <GlassCard ref={chartRef} variant="default" className="card-lift">
      <CardHeader>
        <CardTitle>Temperature Monitoring</CardTitle>
        <CardDescription>Real-time temperature readings from all sensors</CardDescription>
      </CardHeader>
      <CardContent>
        {/* Current Temperature Display */}
        <div className={`mb-6 p-6 rounded-xl bg-gradient-to-br ${status.bgGradient} border border-white/20`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-2">Current Temperature</p>
              <div className="flex items-baseline gap-2">
                <span className="text-6xl font-bold">
                  <CounterValue value={currentTemp} decimals={1} />
                </span>
                <span className="text-3xl text-muted-foreground">°F</span>
              </div>
              <p className={`text-lg font-semibold mt-2 ${status.color}`}>
                {status.label}
              </p>
            </div>
            <FloatingElement intensity="medium" duration={4}>
              <div className={`p-4 rounded-full ${
                status.status === 'safe' ? 'bg-emerald-500/20 glow-emerald' :
                status.status === 'warning' ? 'bg-amber-500/20 glow-amber' :
                'bg-rose-500/20 glow-rose'
              }`}>
                <Thermometer className={`h-16 w-16 ${status.color}`} />
              </div>
            </FloatingElement>
          </div>
        </div>

        {/* Chart */}
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={readings}>
              <defs>
                <linearGradient id="gradientLine" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="opacity-30" />
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
                  backgroundColor: 'rgba(15, 15, 25, 0.9)',
                  border: '1px solid rgba(139, 92, 246, 0.3)',
                  borderRadius: '8px',
                  color: '#fff',
                  backdropFilter: 'blur(8px)',
                }}
                labelFormatter={(value) => `Time: ${value}`}
              />
              <Line
                type="monotone"
                dataKey="temperature"
                stroke="url(#gradientLine)"
                strokeWidth={3}
                stroke="#8b5cf6"
                dot={false}
                activeDot={{ r: 6, stroke: '#8b5cf6', strokeWidth: 2, fill: '#fff' }}
                animationDuration={1500}
                animationBegin={0}
              />
              <Legend />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Safe Range Indicator */}
        <div className="mt-4 flex items-center justify-between text-sm">
          <span className="text-muted-foreground font-medium">Safe range:</span>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30">
              <div className="w-3 h-3 rounded-full bg-emerald-500 glow-emerald" />
              <span className="font-medium">33°F - 41°F</span>
            </div>
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-violet-500" />
              <span className="text-muted-foreground">Updates every 5 min</span>
            </div>
          </div>
        </div>
      </CardContent>
    </GlassCard>
  );
}
