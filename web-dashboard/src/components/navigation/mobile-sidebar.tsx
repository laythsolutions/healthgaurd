'use client';

import { cn } from '@/lib/utils';
import { useRole } from '@/hooks/use-role';
import { getRoleTheme } from '@/lib/role-config';
import { useSidebar } from '@/hooks/use-sidebar';
import { Sheet, SheetContent } from '@/components/ui/sheet';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { TooltipProvider } from '@/components/ui/tooltip';
import { navConfig } from './nav-config';
import { SidebarBrand } from './sidebar-brand';
import { SidebarSection } from './sidebar-section';
import { SidebarUser } from './sidebar-user';

export function MobileSidebar() {
  const role = useRole();
  const theme = getRoleTheme(role);
  const { isMobileOpen, setMobileOpen } = useSidebar();
  const sections = navConfig[role];

  return (
    <Sheet open={isMobileOpen} onOpenChange={setMobileOpen}>
      <SheetContent
        side="left"
        className={cn(
          'w-[280px] p-0 border-r-0',
        )}
      >
        <div
          className={cn(
            'absolute inset-0 bg-gradient-to-b',
            theme.sidebarBg
          )}
        />

        {/* Accent line */}
        <div
          className={cn(
            'absolute left-0 top-0 bottom-0 w-[2px] bg-gradient-to-b',
            theme.accentLine
          )}
        />

        <div className="relative flex h-full flex-col overflow-hidden">
          <TooltipProvider>
            <SidebarBrand isExpanded={true} />

            <Separator className="bg-white/10 mx-3" />

            <ScrollArea className="flex-1 py-2">
              {sections.map((section, index) => (
                <div key={index} onClick={() => setMobileOpen(false)}>
                  {index > 0 && (
                    <Separator className="bg-white/10 mx-4 my-2" />
                  )}
                  <SidebarSection section={section} isExpanded={true} />
                </div>
              ))}
            </ScrollArea>

            <Separator className="bg-white/10 mx-3" />

            <SidebarUser isExpanded={true} />
          </TooltipProvider>
        </div>
      </SheetContent>
    </Sheet>
  );
}
