'use client';

/**
 * Chart Renderer Factory
 *
 * Dynamically renders appropriate chart type based on configuration.
 * Connects dashboard YAML definitions to React components.
 */

import React from 'react';
import { LineChart } from './line-chart';
import { BarChart } from './bar-chart';
import { AreaChart } from './area-chart';
import { TableChart, type Column } from './table-chart';
import { KPITile, kpiFormatters } from './kpi-tile';
import { ChartSkeleton } from './chart-container';

export type ChartType = 'line' | 'bar' | 'area' | 'table' | 'kpi';

interface BaseChartConfig {
  type: ChartType;
  title?: string;
  description?: string;
  footer?: React.ReactNode;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
}

interface LineChartConfig extends BaseChartConfig {
  type: 'line';
  data: Array<Record<string, any>>;
  xKey: string;
  yKeys: string[];
  colors?: string[];
}

interface BarChartConfig extends BaseChartConfig {
  type: 'bar';
  data: Array<Record<string, any>>;
  xKey: string;
  yKeys: string[];
  colors?: string[];
  horizontal?: boolean;
}

interface AreaChartConfig extends BaseChartConfig {
  type: 'area';
  data: Array<Record<string, any>>;
  xKey: string;
  yKeys: string[];
  colors?: string[];
  stacked?: boolean;
}

interface TableChartConfig extends BaseChartConfig {
  type: 'table';
  data: Array<Record<string, any>>;
  columns: Column[];
}

interface KPITileConfig extends BaseChartConfig {
  type: 'kpi';
  value: number | string;
  label: string;
  delta?: number;
  deltaLabel?: string;
  format?: (value: number | string) => string;
  size?: 'small' | 'medium' | 'large';
}

export type ChartConfig =
  | LineChartConfig
  | BarChartConfig
  | AreaChartConfig
  | TableChartConfig
  | KPITileConfig;

/**
 * Render chart based on configuration
 */
export function ChartRenderer({ config }: { config: ChartConfig }) {
  // Show skeleton during loading
  if (config.isLoading) {
    return <ChartSkeleton className={config.className} />;
  }

  switch (config.type) {
    case 'line':
      return (
        <LineChart
          data={config.data}
          xKey={config.xKey}
          yKeys={config.yKeys}
          title={config.title}
          description={config.description}
          footer={config.footer}
          error={config.error}
          className={config.className}
          colors={config.colors}
        />
      );

    case 'bar':
      return (
        <BarChart
          data={config.data}
          xKey={config.xKey}
          yKeys={config.yKeys}
          title={config.title}
          description={config.description}
          footer={config.footer}
          error={config.error}
          className={config.className}
          colors={config.colors}
          horizontal={config.horizontal}
        />
      );

    case 'area':
      return (
        <AreaChart
          data={config.data}
          xKey={config.xKey}
          yKeys={config.yKeys}
          title={config.title}
          description={config.description}
          footer={config.footer}
          error={config.error}
          className={config.className}
          colors={config.colors}
          stacked={config.stacked}
        />
      );

    case 'table':
      return (
        <TableChart
          data={config.data}
          columns={config.columns}
          title={config.title}
          description={config.description}
          footer={config.footer}
          error={config.error}
          className={config.className}
        />
      );

    case 'kpi':
      return (
        <KPITile
          value={config.value}
          label={config.label}
          delta={config.delta}
          deltaLabel={config.deltaLabel}
          format={config.format}
          title={config.title}
          description={config.description}
          error={config.error}
          className={config.className}
          size={config.size}
        />
      );

    default:
      return (
        <div className="rounded-lg border border-border bg-card p-4">
          <p className="text-sm text-muted-foreground">
            Unknown chart type: {(config as any).type}
          </p>
        </div>
      );
  }
}

/**
 * Export formatters for convenience
 */
export { kpiFormatters };
