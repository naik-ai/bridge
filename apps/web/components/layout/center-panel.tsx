'use client';

import * as React from 'react';
import { useAppStore } from '@/lib/store';
import { DashboardView } from '@/components/dashboard/dashboard-view';
import { DashboardEditor } from '@/components/dashboard/dashboard-editor';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LayoutDashboard, Code, Eye } from 'lucide-react';

export function CenterPanel() {
  const { dashboard } = useAppStore();
  const [activeTab, setActiveTab] = React.useState<string>('dashboard');

  return (
    <div className="h-full flex flex-col bg-background">
      {dashboard.viewMode === 'edit' ? (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
          <div className="border-b border-border px-4 py-2">
            <TabsList>
              <TabsTrigger value="dashboard" className="gap-2">
                <LayoutDashboard className="h-4 w-4" />
                Dashboard
              </TabsTrigger>
              <TabsTrigger value="yaml" className="gap-2">
                <Code className="h-4 w-4" />
                YAML
              </TabsTrigger>
              <TabsTrigger value="preview" className="gap-2">
                <Eye className="h-4 w-4" />
                Preview
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="dashboard" className="flex-1 overflow-auto m-0">
            <DashboardEditor />
          </TabsContent>

          <TabsContent value="yaml" className="flex-1 overflow-auto m-0">
            <DashboardEditor mode="yaml" />
          </TabsContent>

          <TabsContent value="preview" className="flex-1 overflow-auto m-0">
            <DashboardView />
          </TabsContent>
        </Tabs>
      ) : (
        <DashboardView />
      )}
    </div>
  );
}
