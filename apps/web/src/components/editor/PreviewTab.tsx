'use client';

import { useState } from 'react';
import { useEditorStore } from '@/lib/store/editor';
import { Button } from '@/components/ui/button';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { RefreshCw } from 'lucide-react';
import type { ViewType } from '@/types/dashboard';

const VIEW_TYPES: { value: ViewType; label: string }[] = [
  { value: 'analytical', label: 'Analytical' },
  { value: 'operational', label: 'Operational' },
  { value: 'strategic', label: 'Strategic' },
];

export function PreviewTab() {
  const { yaml } = useEditorStore();
  const [viewType, setViewType] = useState<ViewType>(
    yaml?.view_type || 'analytical'
  );
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  if (!yaml) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <p>No dashboard loaded</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4 p-4 bg-secondary/20 rounded-lg">
        <div className="flex items-center space-x-4">
          <Label>View Type:</Label>
          <RadioGroup
            value={viewType}
            onValueChange={(value) => setViewType(value as ViewType)}
            className="flex space-x-4"
          >
            {VIEW_TYPES.map((type) => (
              <div key={type.value} className="flex items-center space-x-2">
                <RadioGroupItem value={type.value} id={`view-${type.value}`} />
                <Label htmlFor={`view-${type.value}`} className="cursor-pointer">
                  {type.label}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          className="ml-4"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div
        key={refreshKey}
        className="flex-1 border border-dashed border-border rounded-lg p-8 overflow-auto"
      >
        <div className="space-y-4">
          <div className="text-center">
            <h2 className="text-2xl font-semibold">{yaml.title}</h2>
            <p className="text-sm text-muted-foreground mt-1">
              View: {viewType} • Slug: {yaml.slug}
            </p>
          </div>

          <div className="grid grid-cols-12 gap-4 mt-8">
            {yaml.layout.map((item) => {
              const { position } = item.style;
              return (
                <div
                  key={item.id}
                  className="bg-card border border-border rounded-lg p-4"
                  style={{
                    gridColumn: `span ${position.width}`,
                    minHeight: `${position.height * 80}px`,
                  }}
                >
                  <div className="text-sm font-medium mb-2">{item.id}</div>
                  <div className="text-xs text-muted-foreground mb-4">
                    {item.type} {item.chart && `(${item.chart})`}
                  </div>
                  <div className="border border-dashed border-border rounded h-full flex items-center justify-center text-muted-foreground">
                    Preview
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
