'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useEditorStore, useUnsavedChangesWarning } from '@/lib/store/editor';
import { useDashboard } from '@/hooks/use-dashboards';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft, Clock } from 'lucide-react';
import { BuilderMode } from '@/components/editor/BuilderMode';
import { PropertyInspector } from '@/components/editor/PropertyInspector';
import { YAMLEditor } from '@/components/editor/YAMLEditor';
import { PreviewTab } from '@/components/editor/PreviewTab';
import { SaveWorkflow } from '@/components/editor/SaveWorkflow';
import { format } from 'date-fns';

export default function EditorPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;

  const {
    yaml,
    isDirty,
    lastSaved,
    activeTab,
    setActiveTab,
    setYaml,
    resetEditor,
  } = useEditorStore();

  const { data: dashboard, isLoading, error } = useDashboard(slug);

  useUnsavedChangesWarning();

  useEffect(() => {
    if (dashboard) {
      setYaml(dashboard, JSON.stringify(dashboard));
    }
  }, [dashboard, setYaml]);

  useEffect(() => {
    return () => {
      resetEditor();
    };
  }, [resetEditor]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-destructive mb-4">Failed to load dashboard</p>
          <Button onClick={() => router.push('/dashboards')}>
            Back to Dashboards
          </Button>
        </div>
      </div>
    );
  }

  if (!yaml) {
    return null;
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-border bg-background px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/dashboards">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </Link>

            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-semibold">{yaml.title}</h1>
              {isDirty && (
                <span className="text-xs text-muted-foreground">
                  • Unsaved changes
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {lastSaved && (
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                <span>Saved {format(lastSaved, 'h:mm a')}</span>
              </div>
            )}
            <SaveWorkflow />
          </div>
        </div>
      </header>

      {/* Editor */}
      <div className="flex-1 overflow-hidden">
        <Tabs
          value={activeTab}
          onValueChange={(value) =>
            setActiveTab(value as typeof activeTab)
          }
          className="h-full flex flex-col"
        >
          <TabsList className="w-full justify-start rounded-none border-b border-border">
            <TabsTrigger value="builder">Builder</TabsTrigger>
            <TabsTrigger value="yaml">YAML</TabsTrigger>
            <TabsTrigger value="preview">Preview</TabsTrigger>
          </TabsList>

          <div className="flex-1 overflow-hidden">
            <TabsContent value="builder" className="h-full m-0 p-0">
              <BuilderMode />
            </TabsContent>

            <TabsContent value="yaml" className="h-full m-0 p-6">
              <YAMLEditor />
            </TabsContent>

            <TabsContent value="preview" className="h-full m-0 p-6">
              <PreviewTab />
            </TabsContent>
          </div>
        </Tabs>
      </div>

      {/* Property Inspector */}
      <PropertyInspector />
    </div>
  );
}
