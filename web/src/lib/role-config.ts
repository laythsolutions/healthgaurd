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
    gradient: 'from-indigo-500 to-indigo-400',
    gradientFrom: '#6366f1',
    gradientTo: '#818cf8',
    sidebarBg: 'from-slate-900 to-slate-900',
    activeItemBg: 'bg-indigo-500/15',
    activeItemBorder: 'border-l-indigo-500',
    activeItemGlow: 'shadow-[0_0_12px_rgba(99,102,241,0.25)]',
    iconColor: 'text-indigo-400',
    badgeGradient: 'from-indigo-500 to-indigo-600',
    accentColor: 'indigo',
    hoverBg: 'hover:bg-slate-700/60',
    accentLine: 'from-indigo-500 via-indigo-400 to-blue-500',
  },
  manager: {
    label: 'Manager',
    gradient: 'from-blue-500 to-blue-400',
    gradientFrom: '#3b82f6',
    gradientTo: '#60a5fa',
    sidebarBg: 'from-slate-900 to-slate-900',
    activeItemBg: 'bg-blue-500/15',
    activeItemBorder: 'border-l-blue-500',
    activeItemGlow: 'shadow-[0_0_12px_rgba(59,130,246,0.25)]',
    iconColor: 'text-blue-400',
    badgeGradient: 'from-blue-500 to-blue-600',
    accentColor: 'blue',
    hoverBg: 'hover:bg-slate-700/60',
    accentLine: 'from-blue-500 via-blue-400 to-cyan-500',
  },
  staff: {
    label: 'Staff',
    gradient: 'from-emerald-500 to-emerald-400',
    gradientFrom: '#10b981',
    gradientTo: '#34d399',
    sidebarBg: 'from-slate-900 to-slate-900',
    activeItemBg: 'bg-emerald-500/15',
    activeItemBorder: 'border-l-emerald-500',
    activeItemGlow: 'shadow-[0_0_12px_rgba(16,185,129,0.25)]',
    iconColor: 'text-emerald-400',
    badgeGradient: 'from-emerald-500 to-emerald-600',
    accentColor: 'emerald',
    hoverBg: 'hover:bg-slate-700/60',
    accentLine: 'from-emerald-500 via-emerald-400 to-teal-500',
  },
  inspector: {
    label: 'Inspector',
    gradient: 'from-amber-500 to-amber-400',
    gradientFrom: '#f59e0b',
    gradientTo: '#fbbf24',
    sidebarBg: 'from-slate-900 to-slate-900',
    activeItemBg: 'bg-amber-500/15',
    activeItemBorder: 'border-l-amber-500',
    activeItemGlow: 'shadow-[0_0_12px_rgba(245,158,11,0.25)]',
    iconColor: 'text-amber-400',
    badgeGradient: 'from-amber-500 to-amber-600',
    accentColor: 'amber',
    hoverBg: 'hover:bg-slate-700/60',
    accentLine: 'from-amber-500 via-amber-400 to-orange-500',
  },
};

export function getRoleTheme(role: UserRole): RoleTheme {
  return roleThemes[role] ?? roleThemes.admin;
}
