'use client';

import * as React from 'react';
import { useAppStore } from '@/lib/store';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { LineChart, BarChart, Clock, TrendingUp, RefreshCw } from 'lucide-react';
import { ChartCard } from '@/components/charts/chart-card';
import { FreshnessBadge } from '@/components/ui/freshness-badge';
import { cn } from '@/lib/utils';

interface DashboardData {
  title: string;
  description?: string;
  viewType: 'analytical' | 'operational' | 'strategic';
  lastUpdated: Date;
  charts: ChartItem[];
}

interface ChartItem {
  id: string;
  title: string;
  type: 'kpi' | 'line' | 'bar' | 'area' | 'table';
  size: 'small' | 'medium' | 'large' | 'xlarge';
  data: any[];
  lastUpdated: Date;
}

// Sample dashboard data
const sampleDashboard: DashboardData = {
  title: 'Revenue Dashboard',
  description: 'Track revenue metrics and trends across regions',
  viewType: 'analytical',
  lastUpdated: new Date(Date.now() - 1000 * 60 * 15), // 15 minutes ago
  charts: [
    {
      id: 'revenue_total',
      title: 'Total Revenue',
      type: 'kpi',
      size: 'small',
      lastUpdated: new Date(Date.now() - 1000 * 60 * 15),
      data: [{ value: 1250000, change: 12.5 }],
    },
    {
      id: 'revenue_trend',
      title: 'Revenue Trend',
      type: 'line',
      size: 'medium',
      lastUpdated: new Date(Date.now() - 1000 * 60 * 30),
      data: Array.from({ length: 30 }, (_, i) => ({
        date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        revenue: 35000 + Math.random() * 15000,
        region: i % 2 === 0 ? 'US' : 'EU',
      })),
    },
    {
      id: 'revenue_by_region',
      title: 'Revenue by Region',
      type: 'bar',
      size: 'medium',
      lastUpdated: new Date(Date.now() - 1000 * 60 * 45),
      data: [
        { region: 'US', revenue: 450000 },
        { region: 'EU', revenue: 380000 },
        { region: 'APAC', revenue: 290000 },
        { region: 'LATAM', revenue: 130000 },
      ],
    },
  ],
};

export function DashboardView() {
  const { dashboard } = useAppStore();
  const [data, setData] = React.useState<DashboardData>(sampleDashboard);
  const [isRefreshing, setIsRefreshing] = React.useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate refresh
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsRefreshing(false);
  };

  const getGridCols = (size: string) => {
    switch (size) {
      case 'small':
        return 'col-span-3';
      case 'medium':
        return 'col-span-6';
      case 'large':
        return 'col-span-9';
      case 'xlarge':
        return 'col-span-12';
      default:
        return 'col-span-6';
    }
  };

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Dashboard Header */}
      <div className="border-b border-border px-6 py-4">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-semibold">{data.title}</h1>
            {data.description && (
              <p className="text-sm text-muted-foreground mt-1">{data.description}</p>
            )}
            <div className="flex items-center gap-3 mt-3">
              <FreshnessBadge timestamp={data.lastUpdated} />
              <Badge variant="outline">{data.viewType}</Badge>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="gap-2"
          >
            <RefreshCw className={cn('h-4 w-4', isRefreshing && 'animate-spin')} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Dashboard Grid */}
      <ScrollArea className="flex-1">
        <div className="p-6">
          <div className="grid grid-cols-12 gap-4">
            {data.charts.map((chart) => (
              <div key={chart.id} className={cn(getGridCols(chart.size))}>
                <ChartCard
                  title={chart.title}
                  type={chart.type}
                  data={chart.data}
                  lastUpdated={chart.lastUpdated}
                />
              </div>
            ))}
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}
