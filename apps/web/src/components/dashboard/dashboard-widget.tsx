/**
 * Dashboard Widget Component
 *
 * Wraps chart components with metadata (freshness, source info).
 * Manages widget-level state and interactions.
 */

'use client';

import React from 'react';
import { ChartRenderer, type ChartConfig } from '@/components/charts/chart-renderer';
import { FreshnessIndicator } from './freshness-indicator';
import { cn } from '@/lib/utils';

export interface DashboardWidgetProps {
  config: ChartConfig;
  /**
   * Data freshness timestamp
   */
  asOf?: Date | string;
  /**
   * Source table or materialized view name
   */
  source?: string;
  /**
   * Widget position in grid (for responsive layout)
   */
  position?: {
    row: number;
    col: number;
    width: number;
    height: number;
  };
  /**
   * Manual refresh handler
   */
  onRefresh?: () => void;
  className?: string;
}

export function DashboardWidget({
  config,
  asOf,
  source,
  position,
  onRefresh,
  className,
}: DashboardWidgetProps) {
  // Enhance chart config with footer containing freshness indicator
  const enhancedConfig: ChartConfig = {
    ...config,
    footer: (
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          {asOf && (
            <FreshnessIndicator
              timestamp={asOf}
              format="relative"
              size="small"
            />
          )}
          {source && (
            <span className="hidden sm:inline">
              Source: <code className="font-mono text-xs">{source}</code>
            </span>
          )}
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            className="text-xs hover:text-foreground transition-colors"
            aria-label="Refresh data"
          >
            Refresh
          </button>
        )}
      </div>
    ),
  };

  // Calculate grid-based CSS classes if position provided
  const gridClasses = position
    ? cn(
        'col-span-12',
        `md:col-span-${position.width}`,
        `md:col-start-${position.col + 1}`,
        `md:row-start-${position.row + 1}`,
        `md:row-span-${position.height}`
      )
    : '';

  return (
    <div className={cn(gridClasses, className)}>
      <ChartRenderer config={enhancedConfig} />
    </div>
  );
}
