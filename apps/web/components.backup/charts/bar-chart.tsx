'use client';

import * as React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell,
} from 'recharts';

interface BarChartComponentProps {
  data: any[];
  xKey?: string;
  yKey?: string;
  horizontal?: boolean;
}

export function BarChartComponent({
  data,
  xKey = 'region',
  yKey = 'revenue',
  horizontal = false,
}: BarChartComponentProps) {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <div className="bg-background border border-border rounded-md shadow-lg p-3">
        <p className="text-sm font-medium mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-muted-foreground">{entry.name}:</span>
            <span className="font-medium tabular-nums">
              {new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 0,
              }).format(entry.value)}
            </span>
          </div>
        ))}
      </div>
    );
  };

  // Generate subtle grey shades for bars (monotone theme)
  const colors = [
    'hsl(0 0% 20%)',
    'hsl(0 0% 35%)',
    'hsl(0 0% 50%)',
    'hsl(0 0% 65%)',
    'hsl(0 0% 80%)',
  ];

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} layout={horizontal ? 'vertical' : 'horizontal'}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
        {horizontal ? (
          <>
            <XAxis
              type="number"
              className="text-xs"
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
              tickFormatter={(value) =>
                new Intl.NumberFormat('en-US', {
                  notation: 'compact',
                  compactDisplay: 'short',
                }).format(value)
              }
            />
            <YAxis type="category" dataKey={xKey} className="text-xs" tick={{ fill: 'hsl(var(--muted-foreground))' }} />
          </>
        ) : (
          <>
            <XAxis dataKey={xKey} className="text-xs" tick={{ fill: 'hsl(var(--muted-foreground))' }} />
            <YAxis
              className="text-xs"
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
              tickFormatter={(value) =>
                new Intl.NumberFormat('en-US', {
                  notation: 'compact',
                  compactDisplay: 'short',
                }).format(value)
              }
            />
          </>
        )}
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey={yKey} radius={[4, 4, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
