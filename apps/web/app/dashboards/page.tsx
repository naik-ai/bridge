/**
 * Dashboards Gallery Page
 *
 * Displays all dashboards in a grid layout.
 * Uses typed DashboardMetadata from generated API client.
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { Plus, Calendar, User } from 'lucide-react';
import { DashboardsService } from '@peter/api-client';
import type { DashboardMetadata } from '@peter/api-client';
import { AppShell } from '@/components/layout/app-shell';
import { Button } from '@/components/ui/button';
import { queryKeys } from '@/lib/query-client';
import { cn } from '@/lib/utils';

export default function DashboardsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.dashboards.all,
    queryFn: () => DashboardsService.listDashboards(),
  });

  const dashboards = data?.dashboards ?? [];

  return (
    <AppShell>
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-7xl p-8">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-semibold">Dashboards</h1>
              <p className="mt-1 text-sm text-muted-foreground">
                View and manage your data dashboards
              </p>
            </div>
            <Button asChild>
              <Link href="/dashboards/new">
                <Plus className="mr-2 h-4 w-4" />
                New Dashboard
              </Link>
            </Button>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-48 animate-pulse rounded-lg bg-muted" />
              ))}
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="rounded-lg border border-border bg-card p-8 text-center">
              <p className="text-sm text-muted-foreground">
                Failed to load dashboards. Please try again.
              </p>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !error && dashboards.length === 0 && (
            <div className="rounded-lg border border-dashed border-border bg-card p-12 text-center">
              <h3 className="text-lg font-medium">No dashboards yet</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Get started by creating your first dashboard
              </p>
              <Button className="mt-4" asChild>
                <Link href="/dashboards/new">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Dashboard
                </Link>
              </Button>
            </div>
          )}

          {/* Dashboard Grid */}
          {!isLoading && !error && dashboards.length > 0 && (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {dashboards.map((dashboard) => (
                <DashboardCard key={dashboard.slug} dashboard={dashboard} />
              ))}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}

function DashboardCard({ dashboard }: { dashboard: DashboardMetadata }) {
  return (
    <Link
      href={`/dash/${dashboard.slug}`}
      className="group rounded-lg border border-border bg-card p-6 transition-colors hover:bg-muted"
    >
      <div className="flex flex-col space-y-3">
        <div>
          <h3 className="font-medium group-hover:underline">{dashboard.name}</h3>
          <p className="mt-1 text-sm text-muted-foreground">{dashboard.slug}</p>
        </div>

        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-1">
            <User className="h-3 w-3" />
            <span>{dashboard.owner_email}</span>
          </div>
        </div>

        {dashboard.view_type && (
          <div className="inline-flex w-fit rounded-md border border-border px-2 py-1 text-xs">
            {dashboard.view_type}
          </div>
        )}
      </div>
    </Link>
  );
}
