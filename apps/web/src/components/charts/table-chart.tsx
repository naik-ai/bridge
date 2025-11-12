'use client';

/**
 * Table Chart Component
 *
 * Tabular data visualization with sorting, monotone theme.
 * Supports column configuration and responsive behavior.
 */

import React, { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { ChartContainer } from './chart-container';
import { Button } from '@/components/ui/button';

type SortDirection = 'asc' | 'desc' | null;

export interface Column {
  key: string;
  label: string;
  sortable?: boolean;
  format?: (value: any) => string;
}

interface TableChartProps {
  data: Array<Record<string, any>>;
  columns: Column[];
  title?: string;
  description?: string;
  footer?: React.ReactNode;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
}

export function TableChart({
  data,
  columns,
  title,
  description,
  footer,
  isLoading = false,
  error = null,
  className,
}: TableChartProps) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);

  const sortedData = useMemo(() => {
    if (!sortKey || !sortDirection) return data;

    return [...data].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];

      if (aVal === bVal) return 0;

      const comparison = aVal < bVal ? -1 : 1;
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [data, sortKey, sortDirection]);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      // Cycle through: asc → desc → null
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortDirection(null);
        setSortKey(null);
      }
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const SortIcon = ({ column }: { column: Column }) => {
    if (!column.sortable) return null;

    const isSorted = sortKey === column.key;

    if (!isSorted) {
      return <ArrowUpDown className="ml-2 h-4 w-4" />;
    }

    return sortDirection === 'asc' ? (
      <ArrowUp className="ml-2 h-4 w-4" />
    ) : (
      <ArrowDown className="ml-2 h-4 w-4" />
    );
  };

  return (
    <ChartContainer
      title={title}
      description={description}
      footer={footer}
      isLoading={isLoading}
      error={error}
      className={className}
    >
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((column) => (
                <TableHead key={column.key}>
                  {column.sortable ? (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="-ml-3 h-8 data-[state=open]:bg-accent"
                      onClick={() => handleSort(column.key)}
                    >
                      {column.label}
                      <SortIcon column={column} />
                    </Button>
                  ) : (
                    column.label
                  )}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedData.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No data available
                </TableCell>
              </TableRow>
            ) : (
              sortedData.map((row, index) => (
                <TableRow key={index}>
                  {columns.map((column) => (
                    <TableCell key={column.key} className="font-mono text-sm">
                      {column.format
                        ? column.format(row[column.key])
                        : row[column.key]?.toString() ?? '-'}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </ChartContainer>
  );
}
