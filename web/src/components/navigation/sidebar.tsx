'use client';

import { ChevronLeft } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRole } from '@/hooks/use-role';
import { getRoleTheme } from '@/lib/role-config';
import { useSidebar } from '@/hooks/use-sidebar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { TooltipProvider } from '@/components/ui/tooltip';
import { navConfig } from './nav-config';
import { SidebarBrand } from './sidebar-brand';
import { SidebarSection } from './sidebar-section';
import { SidebarUser } from './sidebar-user';

export function Sidebar() {
  const role = useRole();
  const theme = getRoleTheme(role);
  const { isExpanded, toggle } = useSidebar();
  const sections = navConfig[role];

  return (
    <TooltipProvider>
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 flex flex-col border-r border-gray-100 transition-all duration-300 ease-in-out hidden md:flex',
          isExpanded ? 'w-[var(--sidebar-width)]' : 'w-[var(--sidebar-collapsed-width)]'
        )}
      >
        {/* Background gradient */}
        <div
          className={cn(
            'absolute inset-0 bg-gradient-to-b',
            theme.sidebarBg
          )}
        />

        {/* Animated accent line on left edge */}
        <div
          className={cn(
            'absolute left-0 top-0 bottom-0 w-[2px] bg-gradient-to-b',
            theme.accentLine
          )}
          style={{ backgroundSize: '100% 200%', animation: 'gradient-shift 3s ease infinite' }}
        />

        {/* Content */}
        <div className="relative flex flex-1 flex-col overflow-hidden">
          {/* Brand */}
          <SidebarBrand isExpanded={isExpanded} />

          <Separator className="bg-gray-100 mx-3" />

          {/* Nav sections */}
          <ScrollArea className="flex-1 py-2">
            {sections.map((section, index) => (
              <div key={index}>
                {index > 0 && (
                  <Separator className="bg-gray-100 mx-4 my-2" />
                )}
                <SidebarSection section={section} isExpanded={isExpanded} />
              </div>
            ))}
          </ScrollArea>

          <Separator className="bg-gray-100 mx-3" />

          {/* User */}
          <SidebarUser isExpanded={isExpanded} />

          {/* Collapse toggle */}
          <div className="px-3 pb-3">
            <button
              onClick={toggle}
              className={cn(
                'flex h-9 w-full items-center justify-center rounded-lg border border-gray-200 text-gray-400 transition-all duration-200 hover:bg-gray-50 hover:text-gray-700',
              )}
            >
              <ChevronLeft
                className={cn(
                  'h-4 w-4 transition-transform duration-300',
                  !isExpanded && 'rotate-180'
                )}
              />
            </button>
          </div>
        </div>
      </aside>
    </TooltipProvider>
  );
}
