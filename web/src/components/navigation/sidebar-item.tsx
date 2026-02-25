'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useRole } from '@/hooks/use-role';
import { getRoleTheme } from '@/lib/role-config';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import type { NavItem } from './nav-config';

interface SidebarItemProps {
  item: NavItem;
  isExpanded: boolean;
}

export function SidebarItem({ item, isExpanded }: SidebarItemProps) {
  const pathname = usePathname();
  const role = useRole();
  const theme = getRoleTheme(role);

  const isActive =
    pathname === item.href ||
    (item.href !== `/dashboard/${role}` && pathname.startsWith(item.href + '/'));

  const Icon = item.icon;

  const content = (
    <Link
      href={item.href}
      className={cn(
        'group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
        isExpanded ? 'mx-3' : 'mx-auto w-12 justify-center',
        isActive
          ? cn(
              theme.activeItemBg,
              theme.activeItemGlow,
              'border-l-[3px]',
              theme.activeItemBorder,
              'text-gray-900 font-semibold'
            )
          : cn(
              'border-l-[3px] border-l-transparent text-gray-500',
              theme.hoverBg,
              'hover:text-gray-900'
            )
      )}
    >
      <Icon
        className={cn(
          'h-5 w-5 shrink-0 transition-all duration-200',
          isActive
            ? theme.iconColor
            : 'text-gray-400 group-hover:text-gray-600 group-hover:scale-110'
        )}
      />
      {isExpanded && (
        <span className="truncate">{item.label}</span>
      )}
      {isExpanded && item.badge && (
        <span
          className={cn(
            'ml-auto flex h-5 min-w-[20px] items-center justify-center rounded-full bg-gradient-to-r px-1.5 text-[10px] font-bold text-white',
            theme.badgeGradient
          )}
        >
          {item.badge}
        </span>
      )}
    </Link>
  );

  if (!isExpanded) {
    return (
      <Tooltip delayDuration={0}>
        <TooltipTrigger asChild>{content}</TooltipTrigger>
        <TooltipContent side="right" className="flex items-center gap-2">
          {item.label}
          {item.badge && (
            <span className="flex h-4 min-w-[16px] items-center justify-center rounded-full bg-primary px-1 text-[10px] font-bold text-primary-foreground">
              {item.badge}
            </span>
          )}
        </TooltipContent>
      </Tooltip>
    );
  }

  return content;
}
