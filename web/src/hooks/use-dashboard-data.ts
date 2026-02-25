'use client';

import { useState, useEffect } from 'react';

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
    // Simulate API call
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // Mock data for now
        await new Promise((resolve) => setTimeout(resolve, 500));
        setData({
          summary: {
            compliance_score: 94.5,
            active_devices: 12,
            offline_devices: 1,
            critical_alerts: 2,
            avg_temperature: 38.2,
          },
        });
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
