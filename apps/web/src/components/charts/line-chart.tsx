'use client';

/**
 * Line Chart Component
 *
 * Time-series visualization using Recharts with monotone theme.
 * Supports multiple series and responsive behavior.
 */

import React from 'react';
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { ChartContainer } from './chart-container';

interface LineChartProps {
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
}

// Monotone grey palette for multiple series
const DEFAULT_COLORS = [
  'hsl(0, 0%, 10%)',   // Near black
  'hsl(0, 0%, 35%)',   // Dark grey
  'hsl(0, 0%, 50%)',   // Medium grey
  'hsl(0, 0%, 65%)',   // Light grey
  'hsl(0, 0%, 80%)',   // Very light grey
];

export function LineChart({
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
}: LineChartProps) {
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
        <RechartsLineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
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
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          {yKeys.map((key, index) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={colors[index % colors.length]}
              strokeWidth={2}
              dot={{ fill: colors[index % colors.length], r: 3 }}
              activeDot={{ r: 5 }}
            />
          ))}
        </RechartsLineChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
