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

// All roles share a white sidebar base to match the landing page.
// Each role keeps a distinct accent color for active states, icons, and badges.
export const roleThemes: Record<UserRole, RoleTheme> = {
  admin: {
    label: 'Admin',
    gradient: 'from-emerald-600 to-emerald-500',
    gradientFrom: '#059669',
    gradientTo: '#10b981',
    sidebarBg: 'from-white to-white',
    activeItemBg: 'bg-emerald-50',
    activeItemBorder: 'border-l-emerald-600',
    activeItemGlow: 'shadow-none',
    iconColor: 'text-emerald-600',
    badgeGradient: 'from-emerald-600 to-emerald-500',
    accentColor: 'emerald',
    hoverBg: 'hover:bg-gray-50',
    accentLine: 'from-emerald-500 via-emerald-400 to-teal-400',
  },
  manager: {
    label: 'Manager',
    gradient: 'from-blue-600 to-blue-500',
    gradientFrom: '#2563eb',
    gradientTo: '#3b82f6',
    sidebarBg: 'from-white to-white',
    activeItemBg: 'bg-blue-50',
    activeItemBorder: 'border-l-blue-600',
    activeItemGlow: 'shadow-none',
    iconColor: 'text-blue-600',
    badgeGradient: 'from-blue-600 to-blue-500',
    accentColor: 'blue',
    hoverBg: 'hover:bg-gray-50',
    accentLine: 'from-blue-500 via-blue-400 to-cyan-400',
  },
  staff: {
    label: 'Staff',
    gradient: 'from-green-600 to-green-500',
    gradientFrom: '#16a34a',
    gradientTo: '#22c55e',
    sidebarBg: 'from-white to-white',
    activeItemBg: 'bg-green-50',
    activeItemBorder: 'border-l-green-600',
    activeItemGlow: 'shadow-none',
    iconColor: 'text-green-600',
    badgeGradient: 'from-green-600 to-green-500',
    accentColor: 'green',
    hoverBg: 'hover:bg-gray-50',
    accentLine: 'from-green-500 via-emerald-400 to-teal-400',
  },
  inspector: {
    label: 'Inspector',
    gradient: 'from-amber-600 to-amber-500',
    gradientFrom: '#d97706',
    gradientTo: '#f59e0b',
    sidebarBg: 'from-white to-white',
    activeItemBg: 'bg-amber-50',
    activeItemBorder: 'border-l-amber-600',
    activeItemGlow: 'shadow-none',
    iconColor: 'text-amber-600',
    badgeGradient: 'from-amber-600 to-amber-500',
    accentColor: 'amber',
    hoverBg: 'hover:bg-gray-50',
    accentLine: 'from-amber-500 via-amber-400 to-orange-400',
  },
};

export function getRoleTheme(role: UserRole): RoleTheme {
  return roleThemes[role] ?? roleThemes.admin;
}
