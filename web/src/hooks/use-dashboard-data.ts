'use client';

import { useState, useEffect } from 'react';
import { fetchDashboardSummary } from '@/lib/api';

interface DashboardData {
  summary: {
    compliance_score: number;
    active_devices: number;
    offline_devices: number;
    critical_alerts: number;
    avg_temperature: number;
  };
}

export function useDashboardData(restaurantId: string) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const result = await fetchDashboardSummary(restaurantId);
        setData(result);
        setError(null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [restaurantId]);

  return { data, isLoading, error };
}
