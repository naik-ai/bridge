/**
 * TypeScript types for onboarding API.
 */

export type ConnectionType = 'bigquery' | 'postgres' | 'snowflake';
export type ConnectionStatus = 'active' | 'failed' | 'testing';
export type CatalogJobStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface Team {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
}

export interface Connection {
  id: string;
  team_id: string;
  name: string;
  connection_type: ConnectionType;
  status: ConnectionStatus;
  last_tested_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Dataset {
  id: string;
  connection_id: string;
  name: string;
  fully_qualified_name: string;
  description: string | null;
  catalog_job_status: CatalogJobStatus;
  discovered_at: string;
  last_scanned_at: string | null;
}

export interface TableColumn {
  name: string;
  type: string;
  nullable?: boolean;
  description?: string;
}

export interface Table {
  id: string;
  dataset_id: string;
  name: string;
  fully_qualified_name: string;
  description: string | null;
  schema: TableColumn[] | null;
  row_count: number | null;
  size_bytes: number | null;
  discovered_at: string;
  last_scanned_at: string | null;
}

// Request types

export interface TeamCreateRequest {
  name: string;
  slug: string;
}

export interface ConnectionCreateRequest {
  team_id: string;
  name: string;
  connection_type: ConnectionType;
  credentials: Record<string, unknown>;
}

export interface CatalogScanRequest {
  dataset_id: string;
}

// Response types

export interface CatalogScanResponse {
  dataset_id: string;
  status: CatalogJobStatus;
  tables_found: number;
}
