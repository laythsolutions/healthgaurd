import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach JWT token from cookie
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = document.cookie
      .split('; ')
      .find((row) => row.startsWith('access_token='))
      ?.split('=')[1];
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor: handle 401 by redirecting to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Dashboard
export async function fetchDashboardSummary(restaurantId: string) {
  const [sensorsRes, alertsRes] = await Promise.all([
    api.get(`/api/sensors/readings/latest/`, { params: { restaurant: restaurantId } }),
    api.get(`/api/alerts/alerts/summary/`, { params: { restaurant: restaurantId } }),
  ]);

  const readings = sensorsRes.data;
  const alertSummary = alertsRes.data;

  const activeDevices = readings.length;
  const avgTemp = readings.length > 0
    ? readings.reduce((sum: number, r: { temperature?: number }) => sum + (r.temperature || 0), 0) / readings.length
    : 0;

  return {
    summary: {
      compliance_score: 100 - (alertSummary.active_critical * 10 + alertSummary.active_warning * 3),
      active_devices: activeDevices,
      offline_devices: alertSummary.active_warning || 0,
      critical_alerts: alertSummary.active_critical,
      avg_temperature: Math.round(avgTemp * 10) / 10,
    },
  };
}

// Devices
export async function fetchDevices(restaurantId: string) {
  const response = await api.get(`/api/devices/devices/`, {
    params: { restaurant: restaurantId },
  });
  return response.data.results || response.data;
}

export async function createDevice(restaurantId: string, data: Record<string, unknown>) {
  const response = await api.post(`/api/devices/devices/`, {
    ...data,
    restaurant: restaurantId,
  });
  return response.data;
}

export async function updateDevice(deviceId: string, data: Record<string, unknown>) {
  const response = await api.patch(`/api/devices/devices/${deviceId}/`, data);
  return response.data;
}

export async function deleteDevice(deviceId: string) {
  await api.delete(`/api/devices/devices/${deviceId}/`);
}

// Locations
export async function fetchLocations(restaurantId: string) {
  const response = await api.get(`/api/restaurants/restaurants/${restaurantId}/locations/`);
  return response.data.results || response.data;
}

export default api;
