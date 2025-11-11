'use client';

import * as React from 'react';
import { useAppStore } from '@/lib/store';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Code, Copy, Check, FileCode } from 'lucide-react';
import { cn } from '@/lib/utils';

export function YAMLViewer() {
  const { dashboard, setYamlContent } = useAppStore();
  const [copied, setCopied] = React.useState(false);

  const sampleYAML = `version: 0
kind: dashboard
slug: revenue-dashboard
title: "Revenue Dashboard"
owner: user@example.com
view_type: analytical

layout:
  - id: rev_kpi
    type: kpi
    query_ref: q_revenue_total
    style:
      size: small
      position:
        row: 0
        col: 0
        width: 3
        height: 1

  - id: rev_trend
    type: chart
    chart: line
    query_ref: q_revenue_daily
    config:
      x_axis: date
      y_axis: revenue
      series: region
    style:
      color: neutral
      size: medium
      position:
        row: 1
        col: 0
        width: 6
        height: 2

queries:
  - id: q_revenue_total
    warehouse: bigquery
    sql: |
      SELECT SUM(revenue) AS total_revenue
      FROM mart.revenue_daily
      WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)

  - id: q_revenue_daily
    warehouse: bigquery
    sql: |
      SELECT date, region, SUM(revenue) AS revenue
      FROM mart.revenue_daily
      WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
      GROUP BY date, region
      ORDER BY date`;

  const yamlContent = dashboard.yamlContent || sampleYAML;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(yamlContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="h-12 border-b border-border px-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileCode className="h-4 w-4" />
          <span className="font-medium text-sm">YAML</span>
          {dashboard.currentDashboardSlug && (
            <Badge variant="secondary" className="text-xs">
              {dashboard.currentDashboardSlug}
            </Badge>
          )}
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={handleCopy}
          className="h-8 w-8"
          title="Copy YAML"
        >
          {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
        </Button>
      </div>

      {/* YAML Content */}
      <ScrollArea className="flex-1">
        <div className="p-3">
          <pre className="text-xs font-mono text-foreground whitespace-pre-wrap break-words">
            {yamlContent}
          </pre>
        </div>
      </ScrollArea>
    </div>
  );
}
