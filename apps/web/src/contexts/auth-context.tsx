'use client';

/**
 * Authentication Context
 *
 * Provides session management using auto-generated UserInfo type.
 * Integrates with TanStack Query for caching and auto-refresh.
 */

import React, { createContext, useContext, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import type { UserInfo } from '@peter/api-client';
import { AuthService } from '@peter/api-client';
import { queryKeys } from '@/lib/query-client';
import { logout as logoutUtil } from '@/lib/auth';

interface SessionContextValue {
  user: UserInfo | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: Error | null;
  logout: () => Promise<void>;
  refetch: () => void;
}

const SessionContext = createContext<SessionContextValue | undefined>(undefined);

/**
 * Session Provider Component
 *
 * Wraps the app to provide authentication state.
 * Auto-refreshes user info every 5 minutes.
 */
export function SessionProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();

  const {
    data: user,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: queryKeys.auth.me,
    queryFn: async () => {
      try {
        const user = await AuthService.getCurrentUser();
        return user;
      } catch (error) {
        // Not authenticated
        return null;
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
    refetchOnWindowFocus: true,
    retry: false, // Don't retry auth failures
  });

  const logout = useCallback(async () => {
    // Invalidate all queries before logout
    queryClient.clear();
    await logoutUtil();
  }, [queryClient]);

  const value: SessionContextValue = {
    user: user ?? null,
    isLoading,
    isAuthenticated: !!user,
    error: error as Error | null,
    logout,
    refetch: () => {
      refetch();
    },
  };

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

/**
 * Hook to access session state
 *
 * @example
 * const { user, isAuthenticated, logout } = useSession();
 */
export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within SessionProvider');
  }
  return context;
}
