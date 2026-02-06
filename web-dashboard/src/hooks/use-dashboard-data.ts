import { useQuery } from '@tanstack/react-query';
import { analyticsApi, restaurantApi } from '@/lib/api';

export function useDashboardData(restaurantId?: string) {
  const { data: restaurants } = useQuery({
    queryKey: ['restaurants'],
    queryFn: () => restaurantApi.list(),
  });

  const dashboardQuery = useQuery({
    queryKey: ['dashboard', restaurantId],
    queryFn: () => analyticsApi.dashboard(),
    enabled: !!restaurantId,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Get dashboard summary
  const summary = dashboardQuery.data?.[0] || null;

  return {
    restaurants: restaurants?.results || [],
    data: summary,
    isLoading: dashboardQuery.isLoading,
    error: dashboardQuery.error,
  };
}
