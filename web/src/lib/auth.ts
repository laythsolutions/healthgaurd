import { cookies } from 'next/headers';

export interface Session {
  user: {
    id: string;
    email: string;
    name: string;
    role: 'ADMIN' | 'MANAGER' | 'STAFF' | 'INSPECTOR';
    organization_id?: string;
    restaurant_id?: string;
  };
  accessToken: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getServerSession(): Promise<Session | null> {
  const cookieStore = cookies();
  const accessToken = cookieStore.get('access_token')?.value;

  if (!accessToken) {
    return null;
  }

  try {
    const response = await fetch(`${API_URL}/api/accounts/me/`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      return null;
    }

    const user = await response.json();
    return { user, accessToken };
  } catch {
    return null;
  }
}

export async function login(email: string, password: string): Promise<{ access: string; refresh: string }> {
  const response = await fetch(`${API_URL}/api/accounts/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  return response.json();
}

export async function refreshToken(refresh: string): Promise<string> {
  const response = await fetch(`${API_URL}/api/accounts/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    throw new Error('Token refresh failed');
  }

  const data = await response.json();
  return data.access;
}
