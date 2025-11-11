'use client';

import * as React from 'react';
import { useAppStore } from '@/lib/store';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Database,
  Table,
  Search,
  ChevronRight,
  ChevronDown,
  RefreshCw,
  Layers,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface Dataset {
  id: string;
  name: string;
  tables: Table[];
  isExpanded: boolean;
}

interface Table {
  id: string;
  name: string;
  type: 'TABLE' | 'VIEW' | 'MATERIALIZED_VIEW';
  rowCount?: number;
}

export function DatasetBrowser() {
  const { setSelectedDataset, setSelectedTable, dashboard } = useAppStore();
  const [searchQuery, setSearchQuery] = React.useState('');
  const [datasets, setDatasets] = React.useState<Dataset[]>([
    {
      id: 'analytics',
      name: 'analytics',
      isExpanded: true,
      tables: [
        { id: 'users', name: 'users', type: 'TABLE', rowCount: 125000 },
        { id: 'events', name: 'events', type: 'TABLE', rowCount: 5230000 },
        { id: 'revenue_daily', name: 'revenue_daily', type: 'MATERIALIZED_VIEW', rowCount: 365 },
        { id: 'user_activity', name: 'user_activity', type: 'VIEW' },
      ],
    },
    {
      id: 'marketing',
      name: 'marketing',
      isExpanded: false,
      tables: [
        { id: 'campaigns', name: 'campaigns', type: 'TABLE', rowCount: 85 },
        { id: 'ad_spend', name: 'ad_spend', type: 'TABLE', rowCount: 12500 },
      ],
    },
  ]);

  const toggleDataset = (datasetId: string) => {
    setDatasets((prev) =>
      prev.map((ds) =>
        ds.id === datasetId ? { ...ds, isExpanded: !ds.isExpanded } : ds
      )
    );
  };

  const handleTableClick = (datasetName: string, tableName: string) => {
    setSelectedDataset(datasetName);
    setSelectedTable(tableName);
  };

  const handleRefresh = () => {
    // TODO: Implement actual data fetching
    console.log('Refreshing datasets...');
  };

  const filteredDatasets = datasets.map((dataset) => ({
    ...dataset,
    tables: dataset.tables.filter((table) =>
      table.name.toLowerCase().includes(searchQuery.toLowerCase())
    ),
  }));

  const formatRowCount = (count?: number) => {
    if (!count) return '';
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count.toString();
  };

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="h-12 border-b border-border px-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Database className="h-4 w-4" />
          <span className="font-medium text-sm">Datasets</span>
        </div>
        <Button variant="ghost" size="icon" onClick={handleRefresh} className="h-8 w-8">
          <RefreshCw className="h-3.5 w-3.5" />
        </Button>
      </div>

      {/* Search */}
      <div className="p-3 border-b border-border">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search tables..."
            className="pl-9 h-9"
          />
        </div>
      </div>

      {/* Tree */}
      <ScrollArea className="flex-1">
        <div className="p-2">
          {filteredDatasets.map((dataset) => (
            <div key={dataset.id} className="mb-1">
              {/* Dataset */}
              <button
                onClick={() => toggleDataset(dataset.id)}
                className="w-full flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent text-sm transition-colors"
              >
                {dataset.isExpanded ? (
                  <ChevronDown className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                )}
                <Layers className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">{dataset.name}</span>
                <Badge variant="secondary" className="ml-auto text-xs">
                  {dataset.tables.length}
                </Badge>
              </button>

              {/* Tables */}
              {dataset.isExpanded && (
                <div className="ml-6 mt-1 space-y-0.5">
                  {dataset.tables.map((table) => {
                    const isSelected =
                      dashboard.selectedDataset === dataset.name &&
                      dashboard.selectedTable === table.name;

                    return (
                      <button
                        key={table.id}
                        onClick={() => handleTableClick(dataset.name, table.name)}
                        className={cn(
                          'w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-sm transition-colors',
                          isSelected
                            ? 'bg-primary text-primary-foreground'
                            : 'hover:bg-accent'
                        )}
                      >
                        <Table className="h-3.5 w-3.5" />
                        <span className="flex-1 text-left truncate">{table.name}</span>
                        {table.rowCount && (
                          <span className="text-xs opacity-70">
                            {formatRowCount(table.rowCount)}
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
