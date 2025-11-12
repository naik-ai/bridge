export interface DashboardLayout {
  id: string;
  type: 'kpi' | 'chart' | 'table' | 'text';
  query_ref?: string;
  chart?: 'line' | 'bar' | 'area' | 'pie';
  config?: {
    x_axis?: string;
    y_axis?: string;
    series?: string;
  };
  style: {
    size: 'small' | 'medium' | 'large' | 'xlarge';
    color?: 'neutral' | 'success' | 'warning' | 'error';
    position: {
      row: number;
      col: number;
      width: number;
      height: number;
    };
  };
}

export interface DashboardQuery {
  id: string;
  warehouse: 'bigquery';
  sql: string;
}

export interface DashboardYAML {
  version: number;
  kind: 'dashboard';
  slug: string;
  title: string;
  owner: string;
  view_type: 'analytical' | 'operational' | 'strategic';
  layout: DashboardLayout[];
  queries: DashboardQuery[];
}

export interface ChartData {
  timestamp?: string;
  [key: string]: any;
}

export interface ChartPayload {
  query_id: string;
  data: ChartData[];
  metadata: {
    bytes_scanned?: number;
    row_count: number;
    cache_hit: boolean;
  };
}

export interface DatasetMetadata {
  name: string;
  location: string;
  tables: TableMetadata[];
}

export interface TableMetadata {
  name: string;
  type: 'TABLE' | 'VIEW' | 'MATERIALIZED_VIEW';
  row_count?: number;
  size_bytes?: number;
  modified: string;
}

export interface SchemaField {
  name: string;
  type: string;
  mode: 'NULLABLE' | 'REQUIRED' | 'REPEATED';
  description?: string;
}
