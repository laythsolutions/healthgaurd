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

// All roles share the forest-dark sidebar base (#071210 → #060f0d).
// Each role gets a distinct accent color for active state, icons, and badges.
export const roleThemes: Record<UserRole, RoleTheme> = {
  admin: {
    label: 'Admin',
    gradient: 'from-emerald-500 to-emerald-400',
    gradientFrom: '#10b981',
    gradientTo: '#34d399',
    sidebarBg: 'from-[#071210] via-[#060f0d] to-[#071210]',
    activeItemBg: 'bg-emerald-500/15',
    activeItemBorder: 'border-l-emerald-500',
    activeItemGlow: 'shadow-[0_0_12px_rgba(16,185,129,0.25)]',
    iconColor: 'text-emerald-400',
    badgeGradient: 'from-emerald-600 to-emerald-500',
    accentColor: 'emerald',
    hoverBg: 'hover:bg-emerald-900/30',
    accentLine: 'from-emerald-600 via-emerald-400 to-teal-500',
  },
  manager: {
    label: 'Manager',
    gradient: 'from-teal-500 to-cyan-400',
    gradientFrom: '#14b8a6',
    gradientTo: '#22d3ee',
    sidebarBg: 'from-[#071210] via-[#060f0d] to-[#071210]',
    activeItemBg: 'bg-teal-500/15',
    activeItemBorder: 'border-l-teal-500',
    activeItemGlow: 'shadow-[0_0_12px_rgba(20,184,166,0.25)]',
    iconColor: 'text-teal-400',
    badgeGradient: 'from-teal-600 to-cyan-500',
    accentColor: 'teal',
    hoverBg: 'hover:bg-teal-900/30',
    accentLine: 'from-teal-500 via-cyan-400 to-sky-500',
  },
  staff: {
    label: 'Staff',
    gradient: 'from-green-400 to-emerald-300',
    gradientFrom: '#4ade80',
    gradientTo: '#6ee7b7',
    sidebarBg: 'from-[#071210] via-[#060f0d] to-[#071210]',
    activeItemBg: 'bg-green-500/15',
    activeItemBorder: 'border-l-green-400',
    activeItemGlow: 'shadow-[0_0_12px_rgba(74,222,128,0.2)]',
    iconColor: 'text-green-400',
    badgeGradient: 'from-green-500 to-emerald-400',
    accentColor: 'green',
    hoverBg: 'hover:bg-green-900/30',
    accentLine: 'from-green-500 via-emerald-400 to-teal-400',
  },
  inspector: {
    label: 'Inspector',
    gradient: 'from-amber-500 to-amber-400',
    gradientFrom: '#f59e0b',
    gradientTo: '#fbbf24',
    sidebarBg: 'from-[#071210] via-[#060f0d] to-[#071210]',
    activeItemBg: 'bg-amber-500/15',
    activeItemBorder: 'border-l-amber-500',
    activeItemGlow: 'shadow-[0_0_12px_rgba(245,158,11,0.25)]',
    iconColor: 'text-amber-400',
    badgeGradient: 'from-amber-600 to-amber-400',
    accentColor: 'amber',
    hoverBg: 'hover:bg-amber-900/20',
    accentLine: 'from-amber-500 via-amber-400 to-orange-400',
  },
};

export function getRoleTheme(role: UserRole): RoleTheme {
  return roleThemes[role] ?? roleThemes.admin;
}
