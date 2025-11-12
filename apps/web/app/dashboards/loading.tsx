/**
 * Dashboards Loading State
 */

import { AppShell } from '@/components/layout/app-shell';

export default function DashboardsLoading() {
  return (
    <AppShell>
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-7xl p-8">
          <div className="mb-8">
            <div className="h-9 w-48 animate-pulse rounded bg-muted" />
          </div>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-48 animate-pulse rounded-lg bg-muted" />
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
