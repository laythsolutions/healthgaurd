export type UserRole = 'admin' | 'manager' | 'staff' | 'inspector';

export interface RoleTheme {
  label: string;
  gradient: string;
  gradientFrom: string;
  gradientTo: string;
  sidebarBg: string;
  activeItemBg: string;
  activeItemBorder: string;
  activeItemGlow: string;
  iconColor: string;
  badgeGradient: string;
  accentColor: string;
  hoverBg: string;
  accentLine: string;
}

export const roleThemes: Record<UserRole, RoleTheme> = {
  admin: {
    label: 'Admin',
    gradient: 'from-violet-600 to-purple-600',
    gradientFrom: '#7c3aed',
    gradientTo: '#9333ea',
    sidebarBg: 'from-violet-950 via-purple-950 to-indigo-950',
    activeItemBg: 'bg-gradient-to-r from-violet-500/20 to-purple-500/20',
    activeItemBorder: 'border-l-violet-500',
    activeItemGlow: 'shadow-[0_0_12px_rgba(139,92,246,0.3)]',
    iconColor: 'text-violet-400',
    badgeGradient: 'from-violet-500 to-purple-500',
    accentColor: 'violet',
    hoverBg: 'hover:bg-violet-500/10',
    accentLine: 'from-violet-500 via-purple-500 to-indigo-500',
  },
  manager: {
    label: 'Manager',
    gradient: 'from-blue-600 to-cyan-600',
    gradientFrom: '#2563eb',
    gradientTo: '#0891b2',
    sidebarBg: 'from-blue-950 via-cyan-950 to-teal-950',
    activeItemBg: 'bg-gradient-to-r from-blue-500/20 to-cyan-500/20',
    activeItemBorder: 'border-l-blue-500',
    activeItemGlow: 'shadow-[0_0_12px_rgba(59,130,246,0.3)]',
    iconColor: 'text-blue-400',
    badgeGradient: 'from-blue-500 to-cyan-500',
    accentColor: 'blue',
    hoverBg: 'hover:bg-blue-500/10',
    accentLine: 'from-blue-500 via-cyan-500 to-teal-500',
  },
  staff: {
    label: 'Staff',
    gradient: 'from-emerald-600 to-green-600',
    gradientFrom: '#059669',
    gradientTo: '#16a34a',
    sidebarBg: 'from-emerald-950 via-green-950 to-teal-950',
    activeItemBg: 'bg-gradient-to-r from-emerald-500/20 to-green-500/20',
    activeItemBorder: 'border-l-emerald-500',
    activeItemGlow: 'shadow-[0_0_12px_rgba(16,185,129,0.3)]',
    iconColor: 'text-emerald-400',
    badgeGradient: 'from-emerald-500 to-green-500',
    accentColor: 'emerald',
    hoverBg: 'hover:bg-emerald-500/10',
    accentLine: 'from-emerald-500 via-green-500 to-teal-500',
  },
  inspector: {
    label: 'Inspector',
    gradient: 'from-orange-600 to-amber-600',
    gradientFrom: '#ea580c',
    gradientTo: '#d97706',
    sidebarBg: 'from-orange-950 via-amber-950 to-yellow-950',
    activeItemBg: 'bg-gradient-to-r from-orange-500/20 to-amber-500/20',
    activeItemBorder: 'border-l-orange-500',
    activeItemGlow: 'shadow-[0_0_12px_rgba(249,115,22,0.3)]',
    iconColor: 'text-orange-400',
    badgeGradient: 'from-orange-500 to-amber-500',
    accentColor: 'orange',
    hoverBg: 'hover:bg-orange-500/10',
    accentLine: 'from-orange-500 via-amber-500 to-yellow-500',
  },
};

export function getRoleTheme(role: UserRole): RoleTheme {
  return roleThemes[role] ?? roleThemes.admin;
}
