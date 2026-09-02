import { create } from 'zustand';
import type { AuthenticatedUser } from '../../api/types/schemas';
import { removeToken } from './token-storage';

interface AuthState {
  user: AuthenticatedUser | null;
  isAuthenticated: boolean;
  isInitializing: boolean;
  setUser: (user: AuthenticatedUser) => void;
  logout: () => void;
  setInitializing: (val: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isInitializing: true,
  setUser: (user) => set({ user, isAuthenticated: true, isInitializing: false }),
  logout: () => {
    removeToken();
    set({ user: null, isAuthenticated: false, isInitializing: false });
  },
  setInitializing: (val) => set({ isInitializing: val }),
}));
