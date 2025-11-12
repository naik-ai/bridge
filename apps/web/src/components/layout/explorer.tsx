'use client';

/**
 * Explorer Component
 *
 * Left sidebar with dashboard list and search.
 * Uses typed DashboardMetadata from generated API client.
 */

import React, { useState } from 'react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { Search, Plus, FileText } from 'lucide-react';
import { DashboardsService } from '@peter/api-client';
import type { DashboardMetadata } from '@peter/api-client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { queryKeys } from '@/lib/query-client';
import { cn } from '@/lib/utils';

interface ExplorerProps {
  className?: string;
}

export function Explorer({ className }: ExplorerProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.dashboards.all,
    queryFn: () => DashboardsService.listDashboards(),
  });

  const dashboards = data?.dashboards ?? [];

  // Filter dashboards by search query
  const filteredDashboards = dashboards.filter((dashboard) => {
    const query = searchQuery.toLowerCase();
    return (
      dashboard.name.toLowerCase().includes(query) ||
      dashboard.slug.toLowerCase().includes(query)
    );
  });

  return (
    <aside className={cn('flex flex-col border-r border-border bg-background', className)}>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border p-4">
        <h2 className="text-sm font-semibold">Explorer</h2>
        <Button size="icon" variant="ghost" className="h-8 w-8" asChild>
          <Link href="/dashboards/new">
            <Plus className="h-4 w-4" />
          </Link>
        </Button>
      </div>

      {/* Search */}
      <div className="p-4">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search dashboards..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8"
          />
        </div>
      </div>

      {/* Dashboard List */}
      <div className="flex-1 overflow-y-auto px-2">
        {isLoading && (
          <div className="space-y-2 p-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 animate-pulse rounded-md bg-muted" />
            ))}
          </div>
        )}

        {error && (
          <div className="p-4 text-center text-sm text-muted-foreground">
            Failed to load dashboards
          </div>
        )}

        {!isLoading && !error && filteredDashboards.length === 0 && (
          <div className="p-4 text-center text-sm text-muted-foreground">
            {searchQuery ? 'No dashboards found' : 'No dashboards yet'}
          </div>
        )}

        {!isLoading && !error && filteredDashboards.length > 0 && (
          <div className="space-y-1">
            {filteredDashboards.map((dashboard) => (
              <Link
                key={dashboard.slug}
                href={`/dash/${dashboard.slug}`}
                className="flex items-start gap-3 rounded-md p-2 hover:bg-muted"
              >
                <FileText className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div className="flex-1 space-y-1">
                  <p className="text-sm font-medium leading-none">{dashboard.name}</p>
                  <p className="text-xs text-muted-foreground">{dashboard.slug}</p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Recent Section (Stub) */}
      <div className="border-t border-border p-4">
        <h3 className="mb-2 text-xs font-semibold text-muted-foreground">RECENT</h3>
        <p className="text-xs text-muted-foreground">No recent items</p>
      </div>
    </aside>
  );
}
