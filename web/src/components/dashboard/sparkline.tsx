'use client';

import { ResponsiveContainer, LineChart, Line } from 'recharts';
import { cn } from '@/lib/utils';

interface SparklineProps {
  data: number[];
  status?: 'good' | 'warning' | 'critical' | 'neutral';
  color?: string;
  className?: string;
}

const statusColors = {
  good: '#10b981',
  warning: '#f59e0b',
  critical: '#f43f5e',
  neutral: '#8b5cf6',
};

export function Sparkline({
  data,
  status = 'neutral',
  color,
  className,
}: SparklineProps) {
  const chartData = data.map((value, index) => ({ index, value }));
  const strokeColor = color || statusColors[status];

  return (
    <div className={cn('h-8 w-full', className)}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <Line
            type="monotone"
            dataKey="value"
            stroke={strokeColor}
            strokeWidth={1.5}
            dot={false}
            isAnimationActive={true}
            animationDuration={1000}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
