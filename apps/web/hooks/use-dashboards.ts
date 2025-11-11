import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DashboardYAML } from '@/types/dashboard';

// Mock API calls - replace with actual API client calls
const fetchDashboards = async (): Promise<DashboardYAML[]> => {
  // TODO: Replace with actual API call
  await new Promise((resolve) => setTimeout(resolve, 500));
  return [];
};

const fetchDashboard = async (slug: string): Promise<DashboardYAML | null> => {
  // TODO: Replace with actual API call
  await new Promise((resolve) => setTimeout(resolve, 500));
  return null;
};

const saveDashboard = async (dashboard: DashboardYAML): Promise<DashboardYAML> => {
  // TODO: Replace with actual API call
  await new Promise((resolve) => setTimeout(resolve, 500));
  return dashboard;
};

export function useDashboards() {
  return useQuery({
    queryKey: ['dashboards'],
    queryFn: fetchDashboards,
  });
}

export function useDashboard(slug: string | null) {
  return useQuery({
    queryKey: ['dashboard', slug],
    queryFn: () => (slug ? fetchDashboard(slug) : null),
    enabled: !!slug,
  });
}

export function useSaveDashboard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: saveDashboard,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['dashboards'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard', data.slug] });
    },
  });
}
