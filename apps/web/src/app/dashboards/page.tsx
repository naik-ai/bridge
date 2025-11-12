/**
 * Dashboard Gallery Page
 *
 * Lists all available dashboards with metadata.
 * Zero-backend mode: loads from file system.
 */

import React from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TimestampDisplay } from '@/components/dashboard/freshness-indicator';
import { loadDashboardList } from '@/lib/dashboard-loader';
import { BarChart3, TrendingUp, Activity } from 'lucide-react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Dashboards | Peter',
  description: 'Browse all available dashboards',
};

/**
 * Get icon for view type
 */
function getViewTypeIcon(viewType: string) {
  switch (viewType) {
    case 'analytical':
      return <BarChart3 className="h-4 w-4" />;
    case 'operational':
      return <Activity className="h-4 w-4" />;
    case 'strategic':
      return <TrendingUp className="h-4 w-4" />;
    default:
      return <BarChart3 className="h-4 w-4" />;
  }
}

export default async function DashboardsPage() {
  const dashboards = await loadDashboardList();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-3xl font-semibold">Dashboards</h1>
          <p className="mt-2 text-muted-foreground">
            Browse and access all your data dashboards
          </p>
        </div>
      </header>

      {/* Dashboard Grid */}
      <main className="container mx-auto px-4 py-8">
        {dashboards.length === 0 ? (
          <div className="flex min-h-[400px] items-center justify-center">
            <div className="text-center">
              <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground" />
              <h2 className="mt-4 text-lg font-semibold">No dashboards found</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                Create your first dashboard to get started
              </p>
            </div>
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {dashboards.map((dashboard) => (
              <Link
                key={dashboard.slug}
                href={`/dashboards/${dashboard.slug}`}
                className="group transition-transform hover:scale-[1.02]"
              >
                <Card className="h-full transition-shadow group-hover:shadow-md">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg group-hover:text-foreground/80">
                          {dashboard.title}
                        </CardTitle>
                        <CardDescription className="mt-1">
                          {dashboard.owner}
                        </CardDescription>
                      </div>
                      <Badge variant="secondary" className="flex items-center gap-1">
                        {getViewTypeIcon(dashboard.view_type)}
                        <span className="capitalize">{dashboard.view_type}</span>
                      </Badge>
                    </div>
                  </CardHeader>

                  <CardContent>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">
                        {dashboard.chartCount} {dashboard.chartCount === 1 ? 'widget' : 'widgets'}
                      </span>
                      <TimestampDisplay
                        timestamp={dashboard.lastModified}
                        format="relative"
                      />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
