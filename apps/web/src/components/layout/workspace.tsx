/**
 * Workspace Component
 *
 * Center content area for active tabs and content.
 */

import React from 'react';
import { cn } from '@/lib/utils';

interface WorkspaceProps {
  children: React.ReactNode;
  className?: string;
}

export function Workspace({ children, className }: WorkspaceProps) {
  return (
    <main className={cn('flex flex-1 flex-col overflow-hidden bg-background', className)}>
      {children}
    </main>
  );
}
