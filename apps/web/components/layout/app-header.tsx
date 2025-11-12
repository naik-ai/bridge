'use client';

import * as React from 'react';
import { useAppStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Database,
  LayoutDashboard,
  MessageSquare,
  Save,
  Eye,
  Edit3,
  PanelLeftClose,
  PanelLeftOpen,
  PanelRightClose,
  PanelRightOpen,
  AlertCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatRelativeTime } from '@/lib/utils';

export function AppHeader() {
  const {
    dashboard,
    ui,
    toggleLeftPanel,
    toggleRightPanel,
    setViewMode,
  } = useAppStore();

  const handleSave = () => {
    // TODO: Implement save logic
    console.log('Saving dashboard...');
  };

  const toggleMode = () => {
    setViewMode(dashboard.viewMode === 'view' ? 'edit' : 'view');
  };

  return (
    <header className="h-14 border-b border-border bg-background px-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <LayoutDashboard className="h-5 w-5" />
          <span className="font-semibold text-lg">Peter</span>
        </div>

        <Separator orientation="vertical" className="h-6" />

        {/* Panel toggles */}
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleLeftPanel}
            className="h-8 w-8"
            title={ui.isLeftPanelCollapsed ? 'Show explorer' : 'Hide explorer'}
          >
            {ui.isLeftPanelCollapsed ? (
              <PanelLeftOpen className="h-4 w-4" />
            ) : (
              <PanelLeftClose className="h-4 w-4" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleRightPanel}
            className="h-8 w-8"
            title={ui.isRightPanelCollapsed ? 'Show assistant' : 'Hide assistant'}
          >
            {ui.isRightPanelCollapsed ? (
              <PanelRightOpen className="h-4 w-4" />
            ) : (
              <PanelRightClose className="h-4 w-4" />
            )}
          </Button>
        </div>

        <Separator orientation="vertical" className="h-6" />

        {/* Current dashboard */}
        {dashboard.currentDashboardSlug && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {dashboard.currentDashboardSlug}
            </span>
            {dashboard.isDirty && (
              <Badge variant="outline" className="gap-1">
                <AlertCircle className="h-3 w-3" />
                Unsaved
              </Badge>
            )}
          </div>
        )}
      </div>

      <div className="flex items-center gap-2">
        {/* Last saved */}
        {dashboard.lastSaved && (
          <span className="text-xs text-muted-foreground">
            Saved {formatRelativeTime(dashboard.lastSaved)}
          </span>
        )}

        {/* View/Edit mode toggle */}
        <Button
          variant={dashboard.viewMode === 'edit' ? 'default' : 'outline'}
          size="sm"
          onClick={toggleMode}
          className="gap-2"
        >
          {dashboard.viewMode === 'edit' ? (
            <>
              <Edit3 className="h-4 w-4" />
              Edit
            </>
          ) : (
            <>
              <Eye className="h-4 w-4" />
              View
            </>
          )}
        </Button>

        {/* Save button */}
        <Button
          variant="default"
          size="sm"
          onClick={handleSave}
          disabled={!dashboard.isDirty}
          className="gap-2"
        >
          <Save className="h-4 w-4" />
          Save
        </Button>
      </div>
    </header>
  );
}
