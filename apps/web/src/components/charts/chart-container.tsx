/**
 * Chart Container Component
 *
 * Wrapper for all chart types providing consistent layout, loading, and error states.
 * Applies monotone theme and ensures responsive behavior.
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChartContainerProps {
  title?: string;
  description?: string;
  footer?: React.ReactNode;
  children: React.ReactNode;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
}

export function ChartContainer({
  title,
  description,
  footer,
  children,
  isLoading = false,
  error = null,
  className,
}: ChartContainerProps) {
  return (
    <Card className={cn('flex flex-col', className)}>
      {(title || description) && (
        <CardHeader>
          {title && <CardTitle className="text-lg font-semibold">{title}</CardTitle>}
          {description && (
            <CardDescription className="text-sm text-muted-foreground">
              {description}
            </CardDescription>
          )}
        </CardHeader>
      )}

      <CardContent className="flex-1">
        {isLoading && (
          <div className="flex h-full min-h-[200px] items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        )}

        {error && (
          <div className="flex h-full min-h-[200px] flex-col items-center justify-center gap-2 text-center">
            <AlertCircle className="h-8 w-8 text-destructive" />
            <div>
              <p className="font-medium">Failed to load chart</p>
              <p className="text-sm text-muted-foreground">{error}</p>
            </div>
          </div>
        )}

        {!isLoading && !error && children}
      </CardContent>

      {footer && !isLoading && !error && <CardFooter>{footer}</CardFooter>}
    </Card>
  );
}

/**
 * Chart Loading Skeleton
 *
 * Consistent loading state for all chart types.
 */
export function ChartSkeleton({ className }: { className?: string }) {
  return (
    <Card className={cn('flex flex-col', className)}>
      <CardHeader>
        <div className="h-6 w-32 animate-pulse rounded bg-muted" />
        <div className="h-4 w-48 animate-pulse rounded bg-muted" />
      </CardHeader>
      <CardContent>
        <div className="h-[200px] animate-pulse rounded bg-muted" />
      </CardContent>
    </Card>
  );
}
