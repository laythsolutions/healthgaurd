'use client';

import { usePathname } from 'next/navigation';
import type { UserRole } from '@/lib/role-config';

const validRoles: UserRole[] = ['admin', 'manager', 'staff', 'inspector'];

export function useRole(): UserRole {
  const pathname = usePathname();
  const segments = pathname.split('/');
  // URL pattern: /dashboard/{role}/...
  const roleSegment = segments[2] as UserRole | undefined;

  if (roleSegment && validRoles.includes(roleSegment)) {
    return roleSegment;
  }

  return 'admin';
}
