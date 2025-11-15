import { QueryClient } from '@tanstack/react-query'

/**
 * TanStack Query client configuration
 * Global settings for data fetching, caching, and refetching
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Cache data for 5 minutes by default
      staleTime: 1000 * 60 * 5,
      // Keep unused data in cache for 30 minutes
      gcTime: 1000 * 60 * 30,
      // Retry failed requests once
      retry: 1,
      // Don't refetch on window focus in development
      refetchOnWindowFocus: process.env.NODE_ENV === 'production',
    },
    mutations: {
      // Retry failed mutations once
      retry: 1,
    },
  },
})

/**
 * Query keys for TanStack Query
 * Centralized key management for cache invalidation and prefetching
 */
export const queryKeys = {
  all: ['bridge'] as const,
  dashboards: ['bridge', 'dashboards'] as const,
  dashboard: (slug: string) => ['bridge', 'dashboards', slug] as const,
  dashboardData: (slug: string) => ['bridge', 'dashboards', slug, 'data'] as const,
  lineage: (slug: string) => ['bridge', 'lineage', slug] as const,
  datasets: ['bridge', 'datasets'] as const,
  session: (sessionId: string) => ['bridge', 'sessions', sessionId] as const,
  user: ['bridge', 'user'] as const,
}
