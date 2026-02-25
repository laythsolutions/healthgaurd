'use client';

import { useEffect, useState } from 'react';

interface RestaurantSelectProps {
  value: string;
  onChange: (value: string) => void;
}

interface Restaurant {
  id: string;
  name: string;
}

export function RestaurantSelect({ value, onChange }: RestaurantSelectProps) {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);

  useEffect(() => {
    // Mock data for now
    setRestaurants([
      { id: '1', name: 'Downtown Restaurant' },
      { id: '2', name: 'Uptown Cafe' },
      { id: '3', name: 'Harbor View Bistro' },
    ]);
  }, []);

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="border rounded-lg px-3 py-2 bg-background"
    >
      <option value="">Select Restaurant</option>
      {restaurants.map((restaurant) => (
        <option key={restaurant.id} value={restaurant.id}>
          {restaurant.name}
        </option>
      ))}
    </select>
  );
}
