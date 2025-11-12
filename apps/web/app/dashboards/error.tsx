'use client';

/**
 * Dashboards Error Boundary
 */

import { AppShell } from '@/components/layout/app-shell';
import { Button } from '@/components/ui/button';

export default function DashboardsError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <AppShell>
      <div className="flex flex-1 items-center justify-center p-8">
        <div className="text-center">
          <h2 className="text-lg font-semibold">Something went wrong</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            {error.message || 'An unexpected error occurred'}
          </p>
          {error.digest && (
            <p className="mt-1 text-xs text-muted-foreground">Trace ID: {error.digest}</p>
          )}
          <Button onClick={reset} className="mt-4">
            Try again
          </Button>
        </div>
      </div>
    </AppShell>
  );
}
