'use client';

/**
 * App Shell Component
 *
 * Three-panel layout: Explorer | Workspace | Assistant
 * Responsive with collapsible sidebars.
 */

import React, { useState } from 'react';
import { Header } from './header';
import { Explorer } from './explorer';
import { Workspace } from './workspace';
import { Assistant } from './assistant';
import { cn } from '@/lib/utils';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [explorerVisible, setExplorerVisible] = useState(true);
  const [assistantVisible, setAssistantVisible] = useState(false);

  return (
    <div className="flex h-screen flex-col overflow-hidden">
      <Header
        onToggleExplorer={() => setExplorerVisible(!explorerVisible)}
        onToggleAssistant={() => setAssistantVisible(!assistantVisible)}
        explorerVisible={explorerVisible}
        assistantVisible={assistantVisible}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Explorer (Left Sidebar) */}
        <Explorer
          className={cn(
            'w-60 transition-all duration-200',
            !explorerVisible && 'hidden lg:flex'
          )}
        />

        {/* Workspace (Center) */}
        <Workspace className="flex-1">{children}</Workspace>

        {/* Assistant (Right Sidebar) */}
        {assistantVisible && (
          <Assistant
            className={cn('w-80 transition-all duration-200', !assistantVisible && 'hidden')}
          />
        )}
      </div>
    </div>
  );
}
