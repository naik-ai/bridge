/**
 * Dashboard Grid Component
 *
 * Manages 12-column grid layout for dashboard widgets.
 * Supports three view types: Analytical, Operational, Strategic.
 */

'use client';

import React from 'react';
import { DashboardWidget } from './dashboard-widget';
import { type ChartConfig } from '@/components/charts/chart-renderer';
import { type LayoutItem } from '@/lib/yaml-parser';
import { cn } from '@/lib/utils';

export type ViewType = 'analytical' | 'operational' | 'strategic';

export interface DashboardGridProps {
  /**
   * Dashboard widgets to render
   */
  widgets: Array<{
    id: string;
    config: ChartConfig;
    position: {
      row: number;
      col: number;
      width: number;
      height: number;
    };
    asOf?: Date | string;
    source?: string;
  }>;
  /**
   * View type determines layout density and presentation
   */
  viewType?: ViewType;
  /**
   * Global refresh handler
   */
  onRefresh?: (widgetId: string) => void;
  className?: string;
}

/**
 * Get grid configuration based on view type
 */
function getGridConfig(viewType: ViewType) {
  switch (viewType) {
    case 'analytical':
      return {
        gap: 'gap-6',
        density: 'relaxed',
        description: 'Multi-column grid with prominent filters',
      };

    case 'operational':
      return {
        gap: 'gap-4',
        density: 'compact',
        description: 'Status-first with high density',
      };

    case 'strategic':
      return {
        gap: 'gap-8',
        density: 'spacious',
        description: 'Narrative flow with large KPIs',
      };

    default:
      return {
        gap: 'gap-6',
        density: 'balanced',
        description: 'Default balanced layout',
      };
  }
}

export function DashboardGrid({
  widgets,
  viewType = 'analytical',
  onRefresh,
  className,
}: DashboardGridProps) {
  const gridConfig = getGridConfig(viewType);

  return (
    <div
      className={cn(
        'grid grid-cols-12 auto-rows-min',
        gridConfig.gap,
        className
      )}
      data-view-type={viewType}
    >
      {widgets.map((widget) => (
        <DashboardWidget
          key={widget.id}
          config={widget.config}
          position={widget.position}
          asOf={widget.asOf}
          source={widget.source}
          onRefresh={onRefresh ? () => onRefresh(widget.id) : undefined}
        />
      ))}
    </div>
  );
}

/**
 * Dashboard Grid Skeleton
 *
 * Loading state for dashboard grids
 */
export function DashboardGridSkeleton({
  count = 6,
  viewType = 'analytical',
  className,
}: {
  count?: number;
  viewType?: ViewType;
  className?: string;
}) {
  const gridConfig = getGridConfig(viewType);

  return (
    <div
      className={cn(
        'grid grid-cols-12 auto-rows-min',
        gridConfig.gap,
        className
      )}
    >
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className="col-span-12 md:col-span-6 lg:col-span-4"
        >
          <div className="rounded-lg border border-border bg-card p-4">
            <div className="space-y-3">
              <div className="h-5 w-32 animate-pulse rounded bg-muted" />
              <div className="h-[200px] animate-pulse rounded bg-muted" />
              <div className="h-4 w-48 animate-pulse rounded bg-muted" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
