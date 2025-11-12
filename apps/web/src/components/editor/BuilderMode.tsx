'use client';

import { useEditorStore } from '@/lib/store/editor';
import { Card } from '@/components/ui/card';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { LayoutItem } from '@/types/dashboard';

const GRID_COLUMNS = 12;
const COLUMN_WIDTH = 100 / GRID_COLUMNS;

export function BuilderMode() {
  const { yaml, selectedChartId, selectChart } = useEditorStore();

  if (!yaml) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <p>No dashboard loaded</p>
      </div>
    );
  }

  const handleChartClick = (chartId: string) => {
    selectChart(chartId === selectedChartId ? null : chartId);
  };

  const handleKeyDown = (e: React.KeyboardEvent, chartId: string) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleChartClick(chartId);
    } else if (e.key === 'Escape') {
      selectChart(null);
    }
  };

  return (
    <div className="relative w-full h-full p-8 bg-secondary/20">
      {/* Grid overlay */}
      <div className="absolute inset-0 pointer-events-none grid grid-cols-12 gap-0">
        {Array.from({ length: GRID_COLUMNS }).map((_, i) => (
          <div
            key={i}
            className="border-r border-border/20 last:border-r-0"
          />
        ))}
      </div>

      {/* Layout items */}
      <div className="relative">
        {yaml.layout.map((item) => (
          <ChartCard
            key={item.id}
            item={item}
            isSelected={item.id === selectedChartId}
            onClick={() => handleChartClick(item.id)}
            onKeyDown={(e) => handleKeyDown(e, item.id)}
          />
        ))}
      </div>
    </div>
  );
}

interface ChartCardProps {
  item: LayoutItem;
  isSelected: boolean;
  onClick: () => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
}

function ChartCard({ item, isSelected, onClick, onKeyDown }: ChartCardProps) {
  const { position } = item.style;
  
  const style = {
    position: 'absolute' as const,
    left: `${position.col * COLUMN_WIDTH}%`,
    top: `${position.row * 80}px`,
    width: `${position.width * COLUMN_WIDTH}%`,
    height: `${position.height * 80}px`,
  };

  return (
    <Card
      style={style}
      className={cn(
        'cursor-pointer transition-all duration-200',
        'hover:shadow-lg hover:scale-[1.02]',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        isSelected && 'ring-2 ring-primary shadow-lg scale-[1.02]'
      )}
      onClick={onClick}
      onKeyDown={onKeyDown}
      tabIndex={0}
      role="button"
      aria-label={`Select ${item.type} chart ${item.id}`}
      aria-pressed={isSelected}
    >
      <div className="p-4 h-full flex flex-col">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm font-medium">{item.id}</div>
          {isSelected && (
            <Check className="h-4 w-4 text-primary" aria-hidden="true" />
          )}
        </div>
        <div className="text-xs text-muted-foreground mb-2">
          Type: {item.type} {item.chart && `(${item.chart})`}
        </div>
        <div className="flex-1 border border-dashed border-border rounded flex items-center justify-center text-muted-foreground text-sm">
          Chart Preview
        </div>
        <div className="mt-2 text-xs text-muted-foreground">
          Size: {item.style.size} • Color: {item.style.color}
        </div>
      </div>
    </Card>
  );
}
