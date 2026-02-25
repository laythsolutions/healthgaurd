import Link from 'next/link';
import { MapPin, Calendar, Utensils } from 'lucide-react';
import { GradeBadge } from './grade-badge';
import type { Restaurant } from '@/lib/public-api';
import { cn } from '@/lib/utils';

interface RestaurantCardProps {
  restaurant: Restaurant;
}

export function RestaurantCard({ restaurant }: RestaurantCardProps) {
  const isActive = restaurant.status === 'ACTIVE';

  return (
    <Link
      href={`/restaurant/${restaurant.id}`}
      className={cn(
        'group block rounded-2xl border bg-white p-5 shadow-sm transition-all duration-200',
        'hover:shadow-md hover:-translate-y-0.5 hover:border-emerald-200',
        !isActive && 'opacity-60',
      )}
    >
      <div className="flex items-start justify-between gap-4">
        {/* Info */}
        <div className="min-w-0 flex-1">
          <h3 className="truncate font-semibold text-gray-900 group-hover:text-emerald-700 transition-colors">
            {restaurant.name}
          </h3>

          {restaurant.cuisine_type && (
            <div className="mt-0.5 flex items-center gap-1 text-xs text-gray-400">
              <Utensils className="h-3 w-3" />
              {restaurant.cuisine_type}
            </div>
          )}

          <div className="mt-2 flex items-center gap-1 text-sm text-gray-500">
            <MapPin className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">
              {restaurant.address}, {restaurant.city}, {restaurant.state}
            </span>
          </div>

          {restaurant.last_inspection_date && (
            <div className="mt-1 flex items-center gap-1 text-xs text-gray-400">
              <Calendar className="h-3 w-3 shrink-0" />
              Last inspected: {new Date(restaurant.last_inspection_date).toLocaleDateString()}
            </div>
          )}

          {!isActive && (
            <span className="mt-2 inline-block rounded-full bg-red-50 px-2 py-0.5 text-xs font-medium text-red-600">
              {restaurant.status === 'CLOSED' ? 'Closed' : 'Suspended'}
            </span>
          )}
        </div>

        {/* Grade */}
        <div className="shrink-0 flex flex-col items-center gap-1">
          <GradeBadge grade={restaurant.current_grade} size="lg" />
          {restaurant.last_inspection_score !== null && (
            <span className="text-xs text-gray-400">{restaurant.last_inspection_score}/100</span>
          )}
        </div>
      </div>
    </Link>
  );
}

export function RestaurantCardSkeleton() {
  return (
    <div className="animate-pulse rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2">
          <div className="h-4 w-3/4 rounded bg-gray-100" />
          <div className="h-3 w-1/2 rounded bg-gray-100" />
          <div className="h-3 w-2/3 rounded bg-gray-100" />
        </div>
        <div className="h-14 w-14 rounded-full bg-gray-100" />
      </div>
    </div>
  );
}
