'use client';

/**
 * Bar Chart Component
 *
 * Comparison visualization using Recharts with monotone theme.
 * Supports multiple series, horizontal/vertical orientation.
 */

import React from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { ChartContainer } from './chart-container';

interface BarChartProps {
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
  horizontal?: boolean;
}

// Monotone grey palette for multiple series
const DEFAULT_COLORS = [
  'hsl(0, 0%, 10%)',   // Near black
  'hsl(0, 0%, 35%)',   // Dark grey
  'hsl(0, 0%, 50%)',   // Medium grey
  'hsl(0, 0%, 65%)',   // Light grey
  'hsl(0, 0%, 80%)',   // Very light grey
];

export function BarChart({
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
  horizontal = false,
}: BarChartProps) {
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
        <RechartsBarChart
          data={data}
          layout={horizontal ? 'horizontal' : 'vertical'}
          margin={{ top: 5, right: 20, bottom: 5, left: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(0, 0%, 90%)" />
          {horizontal ? (
            <>
              <XAxis
                type="number"
                tick={{ fill: 'hsl(0, 0%, 45%)' }}
                tickLine={{ stroke: 'hsl(0, 0%, 90%)' }}
              />
              <YAxis
                dataKey={xKey}
                type="category"
                tick={{ fill: 'hsl(0, 0%, 45%)' }}
                tickLine={{ stroke: 'hsl(0, 0%, 90%)' }}
              />
            </>
          ) : (
            <>
              <XAxis
                dataKey={xKey}
                tick={{ fill: 'hsl(0, 0%, 45%)' }}
                tickLine={{ stroke: 'hsl(0, 0%, 90%)' }}
              />
              <YAxis
                tick={{ fill: 'hsl(0, 0%, 45%)' }}
                tickLine={{ stroke: 'hsl(0, 0%, 90%)' }}
              />
            </>
          )}
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
            <Bar
              key={key}
              dataKey={key}
              fill={colors[index % colors.length]}
              radius={[4, 4, 0, 0]}
            />
          ))}
        </RechartsBarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
