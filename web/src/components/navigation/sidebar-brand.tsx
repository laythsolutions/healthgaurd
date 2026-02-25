'use client';

import { ShieldCheck } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRole } from '@/hooks/use-role';
import { getRoleTheme } from '@/lib/role-config';

interface SidebarBrandProps {
  isExpanded: boolean;
}

export function SidebarBrand({ isExpanded }: SidebarBrandProps) {
  const role = useRole();
  const theme = getRoleTheme(role);

  return (
    <div className="flex items-center gap-3 px-4 py-5">
      <div
        className={cn(
          'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br shadow-lg transition-transform duration-300 hover:scale-110',
          theme.gradient
        )}
      >
        <ShieldCheck className="h-6 w-6 text-white" />
      </div>
      <div
        className={cn(
          'overflow-hidden transition-all duration-300',
          isExpanded ? 'w-auto opacity-100' : 'w-0 opacity-0'
        )}
      >
        <h1 className="text-lg font-bold text-white whitespace-nowrap">
          HealthGuard
        </h1>
        <p className="text-[11px] font-medium text-white/50 whitespace-nowrap uppercase tracking-wider">
          Compliance Platform
        </p>
      </div>
    </div>
  );
}
