'use client';

import { cn } from '@/lib/utils';
import { useSidebar } from '@/hooks/use-sidebar';
import { AnimatedBackground } from '@/components/layout';
import { Sidebar, Topbar, MobileSidebar } from '@/components/navigation';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isExpanded } = useSidebar();

  return (
    <div className="min-h-screen relative">
      {/* Shared animated background */}
      <AnimatedBackground variant="gradient" />

      {/* Desktop sidebar */}
      <Sidebar />

      {/* Mobile sidebar (sheet) */}
      <MobileSidebar />

      {/* Main content area */}
      <div
        className={cn(
          'flex flex-col transition-all duration-300 ease-in-out min-h-screen',
          'md:ml-[var(--sidebar-width)]',
          !isExpanded && 'md:ml-[var(--sidebar-collapsed-width)]'
        )}
      >
        {/* Topbar */}
        <Topbar />

        {/* Page content */}
        <main className="flex-1 relative z-10 p-4 md:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
