/**
 * Freshness Indicator Component
 *
 * Displays data age with color-coded visual feedback.
 * Follows monotone theme: uses semantic colors only for status.
 */

import React from 'react';
import { Clock } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export interface FreshnessIndicatorProps {
  timestamp: Date | string;
  threshold?: {
    fresh: number;    // minutes (default: 60)
    stale: number;    // minutes (default: 240)
  };
  format?: 'relative' | 'absolute' | 'both';
  size?: 'small' | 'medium';
  className?: string;
}

/**
 * Calculate time difference in minutes
 */
function getMinutesSince(timestamp: Date | string): number {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
  const now = new Date();
  return Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
}

/**
 * Format timestamp as relative time
 */
function formatRelativeTime(minutes: number): string {
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

/**
 * Format timestamp as absolute time
 */
function formatAbsoluteTime(timestamp: Date | string): string {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

/**
 * Get freshness status and color
 */
function getFreshnessStatus(
  minutes: number,
  threshold: { fresh: number; stale: number }
): {
  status: 'fresh' | 'stale' | 'critical' | 'unknown';
  variant: 'default' | 'secondary' | 'destructive';
} {
  if (minutes < 0) {
    return { status: 'unknown', variant: 'secondary' };
  }

  if (minutes < threshold.fresh) {
    return { status: 'fresh', variant: 'default' };
  }

  if (minutes < threshold.stale) {
    return { status: 'stale', variant: 'secondary' };
  }

  return { status: 'critical', variant: 'destructive' };
}

export function FreshnessIndicator({
  timestamp,
  threshold = { fresh: 60, stale: 240 },
  format = 'relative',
  size = 'small',
  className,
}: FreshnessIndicatorProps) {
  const minutesSince = getMinutesSince(timestamp);
  const { status, variant } = getFreshnessStatus(minutesSince, threshold);

  const relativeTime = formatRelativeTime(minutesSince);
  const absoluteTime = formatAbsoluteTime(timestamp);

  const displayText = format === 'relative'
    ? relativeTime
    : format === 'absolute'
    ? absoluteTime
    : `${relativeTime} (${absoluteTime})`;

  const sizeClass = size === 'small' ? 'text-xs' : 'text-sm';

  return (
    <Badge
      variant={variant}
      className={cn(
        'flex items-center gap-1 font-normal',
        sizeClass,
        className
      )}
    >
      <Clock className={size === 'small' ? 'h-3 w-3' : 'h-4 w-4'} />
      <span>{displayText}</span>
    </Badge>
  );
}

/**
 * Standalone timestamp display (no badge styling)
 */
export function TimestampDisplay({
  timestamp,
  format = 'relative',
  className,
}: {
  timestamp: Date | string;
  format?: 'relative' | 'absolute';
  className?: string;
}) {
  const minutesSince = getMinutesSince(timestamp);
  const text = format === 'relative'
    ? formatRelativeTime(minutesSince)
    : formatAbsoluteTime(timestamp);

  return (
    <div className={cn('flex items-center gap-1 text-xs text-muted-foreground', className)}>
      <Clock className="h-3 w-3" />
      <span>{text}</span>
    </div>
  );
}
