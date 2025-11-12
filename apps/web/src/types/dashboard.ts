/**
 * Dashboard type definitions
 * Matches backend YAML schema and frontend state requirements
 */

export type ViewType = 'analytical' | 'operational' | 'strategic';
export type ChartType = 'kpi' | 'line' | 'bar' | 'area' | 'table';
export type SemanticColor = 'neutral' | 'success' | 'warning' | 'error';
export type ChartSize = 'small' | 'medium' | 'large' | 'xlarge';

export interface GridPosition {
  row: number;
  col: number;
  width: number;
  height: number;
}

export interface ChartStyle {
  color: SemanticColor;
  size: ChartSize;
  position: GridPosition;
}

export interface ChartConfig {
  x_axis?: string;
  y_axis?: string;
  series?: string;
  columns?: string[];
}

export interface LayoutItem {
  id: string;
  type: ChartType;
  query_ref: string;
  chart?: ChartType;
  config?: ChartConfig;
  style: ChartStyle;
}

export interface Query {
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
  view_type: ViewType;
  layout: LayoutItem[];
  queries: Query[];
}

export interface EditorState {
  yaml: DashboardYAML | null;
  originalYaml: string | null;
  isDirty: boolean;
  selectedChartId: string | null;
  inspectorOpen: boolean;
  activeTab: 'builder' | 'yaml' | 'preview';
  lastSaved: Date | null;
  validationError: string | null;
}

export interface EditorActions {
  setYaml: (yaml: DashboardYAML, original?: string) => void;
  setYamlText: (text: string) => void;
  updateChart: (chartId: string, updates: Partial<LayoutItem>) => void;
  selectChart: (chartId: string | null) => void;
  toggleInspector: () => void;
  setActiveTab: (tab: EditorState['activeTab']) => void;
  markAsSaved: () => void;
  setValidationError: (error: string | null) => void;
  resetEditor: () => void;
}

export type EditorStore = EditorState & EditorActions;

export interface DashboardListItem {
  slug: string;
  title: string;
  owner: string;
  view_type: ViewType;
  updated_at: string;
  chart_count: number;
}

export interface DashboardAPIError extends Error {
  code: string;
  details?: unknown;
  trace_id?: string;
}
