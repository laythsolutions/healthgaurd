'use client';

import { cn } from '@/lib/utils';
import { SidebarItem } from './sidebar-item';
import type { NavSection } from './nav-config';

interface SidebarSectionProps {
  section: NavSection;
  isExpanded: boolean;
}

export function SidebarSection({ section, isExpanded }: SidebarSectionProps) {
  return (
    <div className="py-2">
      {section.title && isExpanded && (
        <p className="mb-2 px-6 text-[11px] font-semibold uppercase tracking-wider text-white/30">
          {section.title}
        </p>
      )}
      <nav className="flex flex-col gap-1">
        {section.items.map((item) => (
          <SidebarItem key={item.href} item={item} isExpanded={isExpanded} />
        ))}
      </nav>
    </div>
  );
}
