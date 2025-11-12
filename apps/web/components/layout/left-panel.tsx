'use client';

import * as React from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { useAppStore } from '@/lib/store';
import { DatasetBrowser } from '@/components/datasets/dataset-browser';
import { YAMLViewer } from '@/components/yaml/yaml-viewer';

export function LeftPanel() {
  const { ui, setLeftPanelSplitRatio } = useAppStore();

  const handleResize = (sizes: number[]) => {
    if (sizes[0]) {
      setLeftPanelSplitRatio(sizes[0] / 100);
    }
  };

  return (
    <PanelGroup direction="vertical" onLayout={handleResize} className="h-full">
      {/* Dataset Browser - Top */}
      <Panel defaultSize={60} minSize={30} className="flex flex-col">
        <DatasetBrowser />
      </Panel>

      {/* Resize Handle */}
      <PanelResizeHandle className="h-1 bg-border hover:bg-primary/20 active:bg-primary/30 transition-colors cursor-row-resize" />

      {/* YAML Viewer - Bottom */}
      <Panel defaultSize={40} minSize={20} className="flex flex-col">
        <YAMLViewer />
      </Panel>
    </PanelGroup>
  );
}
