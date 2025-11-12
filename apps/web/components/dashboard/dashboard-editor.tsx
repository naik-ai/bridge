'use client';

import * as React from 'react';
import { useAppStore } from '@/lib/store';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { DashboardView } from './dashboard-view';
import { AlertCircle } from 'lucide-react';
import * as YAML from 'yaml';

interface DashboardEditorProps {
  mode?: 'visual' | 'yaml';
}

export function DashboardEditor({ mode = 'visual' }: DashboardEditorProps) {
  const { dashboard, setYamlContent, setDirty } = useAppStore();
  const [localYaml, setLocalYaml] = React.useState(dashboard.yamlContent);
  const [validationError, setValidationError] = React.useState<string | null>(null);

  const handleYamlChange = (value: string) => {
    setLocalYaml(value);
    setDirty(true);

    // Validate YAML
    try {
      YAML.parse(value);
      setValidationError(null);
      setYamlContent(value);
    } catch (error) {
      setValidationError(error instanceof Error ? error.message : 'Invalid YAML syntax');
    }
  };

  if (mode === 'yaml') {
    return (
      <div className="h-full flex flex-col bg-background">
        <ScrollArea className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-4">
            {validationError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{validationError}</AlertDescription>
              </Alert>
            )}
            <Textarea
              value={localYaml}
              onChange={(e) => handleYamlChange(e.target.value)}
              className="font-mono text-sm min-h-[600px] resize-none"
              placeholder="Enter dashboard YAML..."
              spellCheck={false}
            />
          </div>
        </ScrollArea>
      </div>
    );
  }

  return <DashboardView />;
}
