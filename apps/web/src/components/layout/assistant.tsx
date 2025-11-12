'use client';

/**
 * Assistant Component
 *
 * Right panel for LLM chat interface (stub in Phase 2).
 */

import React from 'react';
import { MessageSquare } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AssistantProps {
  className?: string;
}

export function Assistant({ className }: AssistantProps) {
  return (
    <aside className={cn('flex flex-col border-l border-border bg-background', className)}>
      {/* Header */}
      <div className="border-b border-border p-4">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4" />
          <h2 className="text-sm font-semibold">Assistant</h2>
        </div>
      </div>

      {/* Content (Stub) */}
      <div className="flex flex-1 items-center justify-center p-4">
        <div className="text-center">
          <p className="text-sm text-muted-foreground">Assistant coming in Phase 6</p>
        </div>
      </div>

      {/* Input (Stub) */}
      <div className="border-t border-border p-4">
        <div className="rounded-md border border-border bg-muted/50 p-3 text-center text-xs text-muted-foreground">
          Chat interface placeholder
        </div>
      </div>
    </aside>
  );
}
