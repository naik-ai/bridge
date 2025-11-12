'use client';

/**
 * Area Chart Component
 *
 * Trend visualization using Recharts with monotone theme.
 * Shows cumulative or stacked data patterns.
 */

import React from 'react';
import {
  AreaChart as RechartsAreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { ChartContainer } from './chart-container';

interface AreaChartProps {
  data: Array<Record<string, any>>;
  xKey: string;
  yKeys: string[];
  title?: string;
  description?: string;
  footer?: React.ReactNode;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
  colors?: string[];
  stacked?: boolean;
}

// Monotone grey palette with opacity for areas
const DEFAULT_COLORS = [
  'hsl(0, 0%, 10%)',   // Near black
  'hsl(0, 0%, 35%)',   // Dark grey
  'hsl(0, 0%, 50%)',   // Medium grey
  'hsl(0, 0%, 65%)',   // Light grey
  'hsl(0, 0%, 80%)',   // Very light grey
];

export function AreaChart({
  data,
  xKey,
  yKeys,
  title,
  description,
  footer,
  isLoading = false,
  error = null,
  className,
  colors = DEFAULT_COLORS,
  stacked = false,
}: AreaChartProps) {
  return (
    <ChartContainer
      title={title}
      description={description}
      footer={footer}
      isLoading={isLoading}
      error={error}
      className={className}
    >
      <ResponsiveContainer width="100%" height={300}>
        <RechartsAreaChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(0, 0%, 90%)" />
          <XAxis
            dataKey={xKey}
            tick={{ fill: 'hsl(0, 0%, 45%)' }}
            tickLine={{ stroke: 'hsl(0, 0%, 90%)' }}
          />
          <YAxis
            tick={{ fill: 'hsl(0, 0%, 45%)' }}
            tickLine={{ stroke: 'hsl(0, 0%, 90%)' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'hsl(0, 0%, 100%)',
              border: '1px solid hsl(0, 0%, 90%)',
              borderRadius: '4px',
            }}
            labelStyle={{ color: 'hsl(0, 0%, 10%)' }}
          />
          <Legend wrapperStyle={{ paddingTop: '20px' }} />
          {yKeys.map((key, index) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              stackId={stacked ? '1' : undefined}
              stroke={colors[index % colors.length]}
              fill={colors[index % colors.length]}
              fillOpacity={0.6}
            />
          ))}
        </RechartsAreaChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
