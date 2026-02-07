import { create } from 'zustand';

interface SidebarState {
  isExpanded: boolean;
  isMobileOpen: boolean;
  toggle: () => void;
  setExpanded: (expanded: boolean) => void;
  setMobileOpen: (open: boolean) => void;
}

export const useSidebar = create<SidebarState>((set) => ({
  isExpanded: true,
  isMobileOpen: false,
  toggle: () => set((state) => ({ isExpanded: !state.isExpanded })),
  setExpanded: (expanded) => set({ isExpanded: expanded }),
  setMobileOpen: (open) => set({ isMobileOpen: open }),
}));
