/**
 * Dashboard View Page
 *
 * Displays a single dashboard with all its widgets.
 * Loads data from file-based YAML (zero-backend mode).
 */

import React from 'react';
import { notFound } from 'next/navigation';
import { DashboardGrid } from '@/components/dashboard';
import { loadDashboard, loadDashboardData, getMockTimestamp } from '@/lib/dashboard-loader';
import { layoutItemToChartConfig } from '@/lib/yaml-parser';
import type { Metadata } from 'next';

interface DashboardPageProps {
  params: Promise<{
    slug: string;
  }>;
}

/**
 * Generate metadata for SEO
 */
export async function generateMetadata({ params }: DashboardPageProps): Promise<Metadata> {
  const { slug } = await params;
  const dashboard = await loadDashboard(slug);

  if (!dashboard) {
    return {
      title: 'Dashboard Not Found',
    };
  }

  return {
    title: `${dashboard.title} | Peter`,
    description: `View ${dashboard.title} - ${dashboard.layout.length} widgets`,
  };
}

export default async function DashboardPage({ params }: DashboardPageProps) {
  const { slug } = await params;

  // Load dashboard definition
  const dashboard = await loadDashboard(slug);

  if (!dashboard) {
    notFound();
  }

  // Load all query data
  const dataMap = await loadDashboardData(dashboard);

  // Transform layout items to widget configs
  const widgets = dashboard.layout.map((item) => {
    const queryData = dataMap.get(item.query_ref) || [];
    const chartConfig = layoutItemToChartConfig(item, queryData);

    return {
      id: item.id,
      config: chartConfig,
      position: item.position,
      asOf: getMockTimestamp(),
      source: item.query_ref,
    };
  });

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold">{dashboard.title}</h1>
              <p className="text-sm text-muted-foreground">
                {dashboard.owner} • {dashboard.layout.length} widgets
              </p>
            </div>

            <div className="flex items-center gap-2">
              <span className="rounded-md border border-border bg-muted px-3 py-1 text-xs font-medium">
                {dashboard.view_type}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Dashboard Grid */}
      <main className="container mx-auto px-4 py-8">
        <DashboardGrid
          widgets={widgets}
          viewType={dashboard.view_type === 'grid' ? 'analytical' : dashboard.view_type}
        />
      </main>
    </div>
  );
}
