import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';
import type { DashboardYAML, DashboardListItem } from '@/types/dashboard';
import {
  getDashboard,
  listDashboards,
  saveDashboard,
  validateDashboard,
  deleteDashboard,
  DashboardAPIError,
} from '@/lib/api/dashboards';

export function useDashboard(slug: string) {
  return useQuery({
    queryKey: ['dashboard', slug],
    queryFn: () => getDashboard(slug),
    enabled: !!slug,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useDashboards() {
  return useQuery({
    queryKey: ['dashboards'],
    queryFn: listDashboards,
    staleTime: 5 * 60 * 1000,
  });
}

export function useSaveDashboard() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: saveDashboard,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['dashboard', variables.slug] });
      queryClient.invalidateQueries({ queryKey: ['dashboards'] });

      toast({
        title: 'Dashboard saved',
        description: `${variables.title} has been saved successfully.`,
      });
    },
    onError: (error: DashboardAPIError) => {
      toast({
        title: 'Failed to save dashboard',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}

export function useValidateDashboard() {
  return useMutation({
    mutationFn: validateDashboard,
  });
}

export function useDeleteDashboard() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: deleteDashboard,
    onSuccess: (_, slug) => {
      queryClient.invalidateQueries({ queryKey: ['dashboards'] });
      queryClient.removeQueries({ queryKey: ['dashboard', slug] });

      toast({
        title: 'Dashboard deleted',
        description: 'The dashboard has been deleted successfully.',
      });
    },
    onError: (error: DashboardAPIError) => {
      toast({
        title: 'Failed to delete dashboard',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}
