'use client';

import { Menu, Bell } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRole } from '@/hooks/use-role';
import { getRoleTheme } from '@/lib/role-config';
import { useSidebar } from '@/hooks/use-sidebar';
import { usePathname } from 'next/navigation';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { navConfig } from './nav-config';

const userByRole: Record<string, { name: string; initials: string }> = {
  admin: { name: 'Alex Johnson', initials: 'AJ' },
  manager: { name: 'Maria Santos', initials: 'MS' },
  staff: { name: 'Maria', initials: 'M' },
  inspector: { name: 'Robert Chen', initials: 'RC' },
};

function getPageTitle(pathname: string, role: string): string {
  const sections = navConfig[role as keyof typeof navConfig];
  if (!sections) return 'Dashboard';
  for (const section of sections) {
    for (const item of section.items) {
      if (pathname === item.href) return item.label;
    }
  }
  return 'Dashboard';
}

export function Topbar() {
  const role = useRole();
  const theme = getRoleTheme(role);
  const pathname = usePathname();
  const { isExpanded, setMobileOpen } = useSidebar();
  const user = userByRole[role] ?? userByRole.admin;
  const pageTitle = getPageTitle(pathname, role);

  return (
    <header
      className={cn(
        'sticky top-0 z-30 flex h-[var(--topbar-height)] items-center gap-4 border-b px-4 md:px-6 glass-dark'
      )}
    >
      {/* Mobile hamburger */}
      <button
        className="rounded-lg p-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground md:hidden"
        onClick={() => setMobileOpen(true)}
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Page title / breadcrumb */}
      <div className="flex-1">
        <h2
          className={cn(
            'text-lg font-bold bg-gradient-to-r bg-clip-text text-transparent',
            theme.gradient
          )}
        >
          {pageTitle}
        </h2>
      </div>

      {/* Right side actions */}
      <div className="flex items-center gap-3">
        {/* Notification bell */}
        <button className="relative rounded-lg p-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground">
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-rose-400 opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-rose-500" />
          </span>
        </button>

        {/* User dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-2 rounded-lg p-1.5 transition-colors hover:bg-muted">
              <Avatar className="h-8 w-8">
                <AvatarFallback
                  className={cn(
                    'bg-gradient-to-br text-white text-xs font-bold',
                    theme.gradient
                  )}
                >
                  {user.initials}
                </AvatarFallback>
              </Avatar>
              <span className="hidden text-sm font-medium md:block">
                {user.name}
              </span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel>{user.name}</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Log out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
