'use client';

import { useEditorStore } from '@/lib/store/editor';
import { useDebouncedCallback } from '@/lib/utils/debounce';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Separator } from '@/components/ui/separator';
import type { SemanticColor, ChartSize, ChartType } from '@/types/dashboard';

const SEMANTIC_COLORS: { value: SemanticColor; label: string; class: string }[] = [
  { value: 'neutral', label: 'Neutral', class: 'bg-muted' },
  { value: 'success', label: 'Success', class: 'bg-green-500' },
  { value: 'warning', label: 'Warning', class: 'bg-yellow-500' },
  { value: 'error', label: 'Error', class: 'bg-red-500' },
];

const CHART_SIZES: { value: ChartSize; label: string }[] = [
  { value: 'small', label: 'Small' },
  { value: 'medium', label: 'Medium' },
  { value: 'large', label: 'Large' },
  { value: 'xlarge', label: 'X-Large' },
];

const CHART_TYPES: { value: ChartType; label: string }[] = [
  { value: 'kpi', label: 'KPI' },
  { value: 'line', label: 'Line Chart' },
  { value: 'bar', label: 'Bar Chart' },
  { value: 'area', label: 'Area Chart' },
  { value: 'table', label: 'Table' },
];

export function PropertyInspector() {
  const { yaml, selectedChartId, inspectorOpen, toggleInspector, updateChart } =
    useEditorStore();

  const selectedChart = yaml?.layout.find((item) => item.id === selectedChartId);

  const debouncedUpdate = useDebouncedCallback(
    (field: string, value: unknown) => {
      if (selectedChartId) {
        updateChart(selectedChartId, { [field]: value });
      }
    },
    500
  );

  if (!selectedChart) {
    return null;
  }

  const handleColorChange = (color: SemanticColor) => {
    if (selectedChartId) {
      updateChart(selectedChartId, {
        style: { ...selectedChart.style, color },
      });
    }
  };

  const handleSizeChange = (size: ChartSize) => {
    if (selectedChartId) {
      updateChart(selectedChartId, {
        style: { ...selectedChart.style, size },
      });
    }
  };

  const handleChartTypeChange = (chart: ChartType) => {
    if (selectedChartId && selectedChart.type !== 'kpi') {
      updateChart(selectedChartId, { chart });
    }
  };

  return (
    <Sheet open={inspectorOpen} onOpenChange={toggleInspector}>
      <SheetContent className="w-[320px] sm:w-[400px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Chart Properties</SheetTitle>
        </SheetHeader>

        <Tabs defaultValue="appearance" className="mt-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="appearance">Appearance</TabsTrigger>
            <TabsTrigger value="data">Data</TabsTrigger>
            <TabsTrigger value="layout">Layout</TabsTrigger>
          </TabsList>

          <TabsContent value="appearance" className="space-y-6 mt-6">
            <div className="space-y-2">
              <Label htmlFor="chart-id">Chart ID</Label>
              <Input
                id="chart-id"
                value={selectedChart.id}
                onChange={(e) => debouncedUpdate('id', e.target.value)}
              />
            </div>

            <Separator />

            <div className="space-y-3">
              <Label>Color</Label>
              <RadioGroup
                value={selectedChart.style.color}
                onValueChange={handleColorChange}
              >
                {SEMANTIC_COLORS.map((color) => (
                  <div key={color.value} className="flex items-center space-x-2">
                    <RadioGroupItem
                      value={color.value}
                      id={`color-${color.value}`}
                    />
                    <Label
                      htmlFor={`color-${color.value}`}
                      className="flex items-center space-x-2 cursor-pointer"
                    >
                      <div className={`w-4 h-4 rounded ${color.class}`} />
                      <span>{color.label}</span>
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </div>

            <Separator />

            <div className="space-y-3">
              <Label>Size</Label>
              <RadioGroup
                value={selectedChart.style.size}
                onValueChange={handleSizeChange}
              >
                {CHART_SIZES.map((size) => (
                  <div key={size.value} className="flex items-center space-x-2">
                    <RadioGroupItem value={size.value} id={`size-${size.value}`} />
                    <Label
                      htmlFor={`size-${size.value}`}
                      className="cursor-pointer"
                    >
                      {size.label}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </div>

            {selectedChart.type !== 'kpi' && (
              <>
                <Separator />
                <div className="space-y-3">
                  <Label>Chart Type</Label>
                  <RadioGroup
                    value={selectedChart.chart}
                    onValueChange={handleChartTypeChange}
                  >
                    {CHART_TYPES.filter((t) => t.value !== 'kpi').map((type) => (
                      <div key={type.value} className="flex items-center space-x-2">
                        <RadioGroupItem
                          value={type.value}
                          id={`type-${type.value}`}
                        />
                        <Label
                          htmlFor={`type-${type.value}`}
                          className="cursor-pointer"
                        >
                          {type.label}
                        </Label>
                      </div>
                    ))}
                  </RadioGroup>
                </div>
              </>
            )}
          </TabsContent>

          <TabsContent value="data" className="space-y-6 mt-6">
            <div className="space-y-2">
              <Label htmlFor="query-ref">Query Reference</Label>
              <Input
                id="query-ref"
                value={selectedChart.query_ref}
                onChange={(e) => debouncedUpdate('query_ref', e.target.value)}
              />
            </div>

            {selectedChart.config && (
              <>
                {selectedChart.config.x_axis && (
                  <div className="space-y-2">
                    <Label htmlFor="x-axis">X-Axis</Label>
                    <Input
                      id="x-axis"
                      value={selectedChart.config.x_axis}
                      onChange={(e) =>
                        debouncedUpdate('config', {
                          ...selectedChart.config,
                          x_axis: e.target.value,
                        })
                      }
                    />
                  </div>
                )}

                {selectedChart.config.y_axis && (
                  <div className="space-y-2">
                    <Label htmlFor="y-axis">Y-Axis</Label>
                    <Input
                      id="y-axis"
                      value={selectedChart.config.y_axis}
                      onChange={(e) =>
                        debouncedUpdate('config', {
                          ...selectedChart.config,
                          y_axis: e.target.value,
                        })
                      }
                    />
                  </div>
                )}
              </>
            )}
          </TabsContent>

          <TabsContent value="layout" className="space-y-6 mt-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="row">Row</Label>
                <Input
                  id="row"
                  type="number"
                  value={selectedChart.style.position.row}
                  onChange={(e) => {
                    const position = {
                      ...selectedChart.style.position,
                      row: parseInt(e.target.value, 10),
                    };
                    updateChart(selectedChartId!, {
                      style: { ...selectedChart.style, position },
                    });
                  }}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="col">Column</Label>
                <Input
                  id="col"
                  type="number"
                  min={0}
                  max={11}
                  value={selectedChart.style.position.col}
                  onChange={(e) => {
                    const position = {
                      ...selectedChart.style.position,
                      col: parseInt(e.target.value, 10),
                    };
                    updateChart(selectedChartId!, {
                      style: { ...selectedChart.style, position },
                    });
                  }}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="width">Width</Label>
                <Input
                  id="width"
                  type="number"
                  min={1}
                  max={12}
                  value={selectedChart.style.position.width}
                  onChange={(e) => {
                    const position = {
                      ...selectedChart.style.position,
                      width: parseInt(e.target.value, 10),
                    };
                    updateChart(selectedChartId!, {
                      style: { ...selectedChart.style, position },
                    });
                  }}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="height">Height</Label>
                <Input
                  id="height"
                  type="number"
                  min={1}
                  value={selectedChart.style.position.height}
                  onChange={(e) => {
                    const position = {
                      ...selectedChart.style.position,
                      height: parseInt(e.target.value, 10),
                    };
                    updateChart(selectedChartId!, {
                      style: { ...selectedChart.style, position },
                    });
                  }}
                />
              </div>
            </div>

            <div className="text-xs text-muted-foreground">
              <p>Grid: 12 columns × variable rows</p>
              <p className="mt-1">Column: 0-11, Width: 1-12</p>
            </div>
          </TabsContent>
        </Tabs>
      </SheetContent>
    </Sheet>
  );
}
