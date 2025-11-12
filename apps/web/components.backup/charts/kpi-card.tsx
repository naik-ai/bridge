'use client';

import * as React from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { FreshnessBadge } from '@/components/ui/freshness-badge';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface KPICardProps {
  title: string;
  value: number;
  change?: number;
  lastUpdated: Date;
  format?: 'number' | 'currency' | 'percent';
}

export function KPICard({ title, value, change, lastUpdated, format = 'currency' }: KPICardProps) {
  const formatValue = (val: number) => {
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(val);
      case 'percent':
        return `${val.toFixed(1)}%`;
      default:
        return new Intl.NumberFormat('en-US').format(val);
    }
  };

  const getTrendIcon = () => {
    if (!change) return <Minus className="h-4 w-4" />;
    if (change > 0) return <TrendingUp className="h-4 w-4" />;
    return <TrendingDown className="h-4 w-4" />;
  };

  const getTrendColor = () => {
    if (!change) return 'text-muted-foreground';
    if (change > 0) return 'text-success';
    return 'text-error';
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent className="pb-3">
        <div className="flex items-baseline gap-3">
          <span className="text-3xl font-semibold tabular-nums">{formatValue(value)}</span>
          {change !== undefined && (
            <div className={cn('flex items-center gap-1 text-sm font-medium', getTrendColor())}>
              {getTrendIcon()}
              <span>{Math.abs(change).toFixed(1)}%</span>
            </div>
          )}
        </div>
      </CardContent>
      <CardFooter className="pt-0">
        <FreshnessBadge timestamp={lastUpdated} />
      </CardFooter>
    </Card>
  );
}
