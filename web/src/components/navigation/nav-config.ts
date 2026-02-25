import {
  LayoutDashboard,
  Building2,
  Users,
  BarChart3,
  Bell,
  CreditCard,
  Settings,
  HelpCircle,
  Activity,
  ListChecks,
  UserCheck,
  FileText,
  AlertTriangle,
  GraduationCap,
  Calendar,
  ClipboardCheck,
  History,
  ShieldAlert,
  RotateCcw,
  type LucideIcon,
} from 'lucide-react';
import type { UserRole } from '@/lib/role-config';

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  badge?: string;
}

export interface NavSection {
  title?: string;
  items: NavItem[];
}

export const navConfig: Record<UserRole, NavSection[]> = {
  admin: [
    {
      items: [
        { label: 'Overview', href: '/dashboard/admin', icon: LayoutDashboard },
        { label: 'Restaurants', href: '/dashboard/admin/restaurants', icon: Building2 },
        { label: 'Users', href: '/dashboard/admin/users', icon: Users },
        { label: 'Analytics', href: '/dashboard/admin/analytics', icon: BarChart3 },
        { label: 'Alerts', href: '/dashboard/admin/alerts', icon: Bell, badge: '3' },
        { label: 'Billing', href: '/dashboard/admin/billing', icon: CreditCard },
      ],
    },
    {
      items: [
        { label: 'Settings', href: '/dashboard/admin/settings', icon: Settings },
        { label: 'Help', href: '#', icon: HelpCircle },
      ],
    },
  ],
  manager: [
    {
      items: [
        { label: 'Overview', href: '/dashboard/manager', icon: LayoutDashboard },
        { label: 'Sensors', href: '/dashboard/manager/sensors', icon: Activity },
        { label: 'Tasks', href: '/dashboard/manager/tasks', icon: ListChecks, badge: '7' },
        { label: 'Staff', href: '/dashboard/manager/staff', icon: UserCheck },
        { label: 'Logs', href: '/dashboard/manager/logs', icon: FileText },
        { label: 'Reports', href: '/dashboard/manager/reports', icon: FileText },
        { label: 'Alerts', href: '/dashboard/manager/alerts', icon: AlertTriangle, badge: '3' },
      ],
    },
    {
      items: [
        { label: 'Settings', href: '#', icon: Settings },
        { label: 'Help', href: '#', icon: HelpCircle },
      ],
    },
  ],
  staff: [
    {
      items: [
        { label: 'Overview', href: '/dashboard/staff', icon: LayoutDashboard },
        { label: 'My Tasks', href: '/dashboard/staff/tasks', icon: ListChecks, badge: '5' },
        { label: 'Sensors', href: '/dashboard/staff/sensors', icon: Activity },
        { label: 'Alerts', href: '/dashboard/staff/alerts', icon: Bell },
        { label: 'Training', href: '/dashboard/staff/training', icon: GraduationCap },
      ],
    },
    {
      items: [
        { label: 'Help', href: '#', icon: HelpCircle },
      ],
    },
  ],
  inspector: [
    {
      items: [
        { label: 'Overview', href: '/dashboard/inspector', icon: LayoutDashboard },
        { label: 'Schedule', href: '/dashboard/inspector/schedule', icon: Calendar },
        { label: 'Conduct', href: '/dashboard/inspector/conduct', icon: ClipboardCheck },
        { label: 'History', href: '/dashboard/inspector/history', icon: History },
        { label: 'Violations', href: '/dashboard/inspector/violations', icon: ShieldAlert },
        { label: 'Follow-ups', href: '/dashboard/inspector/followups', icon: RotateCcw },
      ],
    },
    {
      items: [
        { label: 'Settings', href: '#', icon: Settings },
        { label: 'Help', href: '#', icon: HelpCircle },
      ],
    },
  ],
};
