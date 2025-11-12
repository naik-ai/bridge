/**
 * TanStack Query hooks for onboarding API operations.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Team,
  TeamCreateRequest,
  Connection,
  ConnectionCreateRequest,
  Dataset,
  Table,
  CatalogScanRequest,
  CatalogScanResponse,
} from '@/types/onboarding';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// API client functions

async function createTeam(data: TeamCreateRequest): Promise<Team> {
  const response = await fetch(`${API_BASE_URL}/onboarding/teams`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create team');
  }

  return response.json();
}

async function listTeams(): Promise<Team[]> {
  const response = await fetch(`${API_BASE_URL}/onboarding/teams`, {
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error('Failed to fetch teams');
  }

  return response.json();
}

async function createConnection(data: ConnectionCreateRequest): Promise<Connection> {
  const response = await fetch(`${API_BASE_URL}/onboarding/connections`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create connection');
  }

  return response.json();
}

async function testConnection(connectionId: string): Promise<Connection> {
  const response = await fetch(
    `${API_BASE_URL}/onboarding/connections/${connectionId}/test`,
    {
      method: 'POST',
      credentials: 'include',
    }
  );

  if (!response.ok) {
    throw new Error('Failed to test connection');
  }

  return response.json();
}

async function listConnections(teamId: string): Promise<Connection[]> {
  const response = await fetch(
    `${API_BASE_URL}/onboarding/connections?team_id=${teamId}`,
    {
      credentials: 'include',
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch connections');
  }

  return response.json();
}

async function discoverDatasets(connectionId: string): Promise<Dataset[]> {
  const response = await fetch(
    `${API_BASE_URL}/onboarding/catalog/discover?connection_id=${connectionId}`,
    {
      method: 'POST',
      credentials: 'include',
    }
  );

  if (!response.ok) {
    throw new Error('Failed to discover datasets');
  }

  return response.json();
}

async function scanDataset(data: CatalogScanRequest): Promise<CatalogScanResponse> {
  const response = await fetch(`${API_BASE_URL}/onboarding/catalog/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Failed to scan dataset');
  }

  return response.json();
}

async function getDatasetTables(datasetId: string): Promise<Table[]> {
  const response = await fetch(
    `${API_BASE_URL}/onboarding/catalog/datasets/${datasetId}/tables`,
    {
      credentials: 'include',
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch tables');
  }

  return response.json();
}

// Hooks

export function useCreateTeam() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createTeam,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams'] });
    },
  });
}

export function useTeams() {
  return useQuery({
    queryKey: ['teams'],
    queryFn: listTeams,
  });
}

export function useCreateConnection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createConnection,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['connections', variables.team_id],
      });
    },
  });
}

export function useTestConnection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: testConnection,
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ['connections', data.team_id],
      });
    },
  });
}

export function useConnections(teamId: string | null) {
  return useQuery({
    queryKey: ['connections', teamId],
    queryFn: () => listConnections(teamId!),
    enabled: !!teamId,
  });
}

export function useDiscoverDatasets() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: discoverDatasets,
    onSuccess: (_, connectionId) => {
      queryClient.invalidateQueries({
        queryKey: ['datasets', connectionId],
      });
    },
  });
}

export function useScanDataset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: scanDataset,
    onSuccess: (response) => {
      queryClient.invalidateQueries({
        queryKey: ['tables', response.dataset_id],
      });
    },
  });
}

export function useDatasetTables(datasetId: string | null) {
  return useQuery({
    queryKey: ['tables', datasetId],
    queryFn: () => getDatasetTables(datasetId!),
    enabled: !!datasetId,
  });
}
