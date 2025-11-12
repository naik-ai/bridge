'use client';

/**
 * KPI Tile Component
 *
 * Single metric display with delta indicator and monotone theme.
 * Supports different sizes and trend visualization.
 */

import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { ChartContainer } from './chart-container';
import { cn } from '@/lib/utils';

interface KPITileProps {
  value: number | string;
  label: string;
  delta?: number;
  deltaLabel?: string;
  format?: (value: number | string) => string;
  title?: string;
  description?: string;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
  size?: 'small' | 'medium' | 'large';
}

export function KPITile({
  value,
  label,
  delta,
  deltaLabel,
  format,
  title,
  description,
  isLoading = false,
  error = null,
  className,
  size = 'medium',
}: KPITileProps) {
  const formattedValue = format ? format(value) : value.toString();

  const deltaColor = delta === undefined || delta === 0
    ? 'text-muted-foreground'
    : delta > 0
    ? 'text-foreground'
    : 'text-foreground';

  const DeltaIcon = delta === undefined || delta === 0
    ? Minus
    : delta > 0
    ? TrendingUp
    : TrendingDown;

  const sizeClasses = {
    small: 'text-2xl',
    medium: 'text-3xl',
    large: 'text-4xl',
  };

  return (
    <ChartContainer
      title={title}
      description={description}
      isLoading={isLoading}
      error={error}
      className={className}
    >
      <div className="flex flex-col gap-2">
        <div className={cn('font-semibold tabular-nums', sizeClasses[size])}>
          {formattedValue}
        </div>

        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">{label}</div>

          {delta !== undefined && (
            <div className={cn('flex items-center gap-1 text-sm font-medium', deltaColor)}>
              <DeltaIcon className="h-4 w-4" />
              <span className="tabular-nums">
                {delta > 0 ? '+' : ''}
                {delta.toFixed(1)}%
              </span>
              {deltaLabel && (
                <span className="text-muted-foreground">
                  {deltaLabel}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </ChartContainer>
  );
}

/**
 * Format helpers for common KPI types
 */
export const kpiFormatters = {
  currency: (value: number | string): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  },

  number: (value: number | string): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('en-US').format(num);
  },

  percentage: (value: number | string): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return `${num.toFixed(1)}%`;
  },

  compact: (value: number | string): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('en-US', {
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(num);
  },
};
