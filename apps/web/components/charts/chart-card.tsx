'use client';

import * as React from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { FreshnessBadge } from '@/components/ui/freshness-badge';
import { LineChartComponent } from './line-chart';
import { BarChartComponent } from './bar-chart';
import { KPICard } from './kpi-card';
import { Skeleton } from '@/components/ui/skeleton';

interface ChartCardProps {
  title: string;
  type: 'kpi' | 'line' | 'bar' | 'area' | 'table';
  data: any[];
  lastUpdated: Date;
  isLoading?: boolean;
  error?: string;
}

export function ChartCard({ title, type, data, lastUpdated, isLoading, error }: ChartCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-48 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-48 text-sm text-muted-foreground">
            {error}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (type === 'kpi') {
    return <KPICard title={title} value={data[0]?.value} change={data[0]?.change} lastUpdated={lastUpdated} />;
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {type === 'line' && <LineChartComponent data={data} />}
        {type === 'bar' && <BarChartComponent data={data} />}
        {type === 'area' && <LineChartComponent data={data} fill />}
      </CardContent>
      <CardFooter className="pt-0">
        <FreshnessBadge timestamp={lastUpdated} />
      </CardFooter>
    </Card>
  );
}
