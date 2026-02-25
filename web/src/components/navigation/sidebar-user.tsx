'use client';

import { LogOut } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRole } from '@/hooks/use-role';
import { getRoleTheme } from '@/lib/role-config';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

interface SidebarUserProps {
  isExpanded: boolean;
}

const userByRole: Record<string, { name: string; initials: string }> = {
  admin: { name: 'Alex Johnson', initials: 'AJ' },
  manager: { name: 'Maria Santos', initials: 'MS' },
  staff: { name: 'Maria', initials: 'M' },
  inspector: { name: 'Robert Chen', initials: 'RC' },
};

export function SidebarUser({ isExpanded }: SidebarUserProps) {
  const role = useRole();
  const theme = getRoleTheme(role);
  const user = userByRole[role] ?? userByRole.admin;

  const content = (
    <div
      className={cn(
        'flex items-center gap-3 px-4 py-3',
        isExpanded ? '' : 'justify-center'
      )}
    >
      <Avatar className="h-9 w-9 shrink-0">
        <AvatarFallback
          className={cn(
            'bg-gradient-to-br text-white text-xs font-bold',
            theme.gradient
          )}
        >
          {user.initials}
        </AvatarFallback>
      </Avatar>
      {isExpanded && (
        <div className="flex-1 overflow-hidden">
          <p className="truncate text-sm font-semibold text-white">
            {user.name}
          </p>
          <span
            className={cn(
              'inline-block rounded-full bg-gradient-to-r px-2 py-0.5 text-[10px] font-bold uppercase text-white',
              theme.badgeGradient
            )}
          >
            {theme.label}
          </span>
        </div>
      )}
      {isExpanded && (
        <button className="rounded-lg p-1.5 text-white/40 transition-colors hover:bg-white/10 hover:text-white">
          <LogOut className="h-4 w-4" />
        </button>
      )}
    </div>
  );

  if (!isExpanded) {
    return (
      <Tooltip delayDuration={0}>
        <TooltipTrigger asChild>{content}</TooltipTrigger>
        <TooltipContent side="right">
          {user.name} ({theme.label})
        </TooltipContent>
      </Tooltip>
    );
  }

  return content;
}
