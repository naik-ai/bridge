'use client';

import * as React from 'react';
import { Badge } from './badge';
import { Clock } from 'lucide-react';
import { getFreshnessLevel, formatRelativeTime, cn } from '@/lib/utils';

interface FreshnessBadgeProps {
  timestamp: Date | string;
  className?: string;
}

export function FreshnessBadge({ timestamp, className }: FreshnessBadgeProps) {
  const level = getFreshnessLevel(timestamp);
  const relativeTime = formatRelativeTime(timestamp);

  const levelStyles = {
    fresh: 'freshness-fresh',
    stale: 'freshness-stale',
    old: 'freshness-old',
    unknown: 'freshness-unknown',
  };

  return (
    <Badge className={cn('freshness-badge', levelStyles[level], className)}>
      <Clock className="h-3 w-3" />
      <span>Updated {relativeTime}</span>
    </Badge>
  );
}
