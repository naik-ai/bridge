'use client';

import * as React from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { useAppStore } from '@/lib/store';
import { LeftPanel } from './left-panel';
import { CenterPanel } from './center-panel';
import { RightPanel } from './right-panel';
import { AppHeader } from './app-header';
import { cn } from '@/lib/utils';

export function AppShell() {
  const { ui, setLeftPanelWidth, setRightPanelWidth } = useAppStore();

  const handleLeftPanelResize = (size: number) => {
    // Panel size is in percentage, convert to approximate pixels (assuming 1440px viewport)
    setLeftPanelWidth((size / 100) * 1440);
  };

  const handleRightPanelResize = (size: number) => {
    setRightPanelWidth((size / 100) * 1440);
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      <AppHeader />
      <div className="flex-1 overflow-hidden">
        <PanelGroup direction="horizontal" className="h-full">
          {/* Left Panel - Explorer */}
          {!ui.isLeftPanelCollapsed && (
            <>
              <Panel
                defaultSize={20}
                minSize={15}
                maxSize={40}
                onResize={handleLeftPanelResize}
                className="border-r border-border"
              >
                <LeftPanel />
              </Panel>
              <PanelResizeHandle className="w-1 bg-border hover:bg-primary/20 active:bg-primary/30 transition-colors cursor-col-resize" />
            </>
          )}

          {/* Center Panel - Workspace */}
          <Panel defaultSize={ui.isLeftPanelCollapsed && ui.isRightPanelCollapsed ? 100 : 60} minSize={30}>
            <CenterPanel />
          </Panel>

          {/* Right Panel - Assistant */}
          {!ui.isRightPanelCollapsed && (
            <>
              <PanelResizeHandle className="w-1 bg-border hover:bg-primary/20 active:bg-primary/30 transition-colors cursor-col-resize" />
              <Panel
                defaultSize={20}
                minSize={20}
                maxSize={40}
                onResize={handleRightPanelResize}
                className="border-l border-border"
              >
                <RightPanel />
              </Panel>
            </>
          )}
        </PanelGroup>
      </div>
    </div>
  );
}
