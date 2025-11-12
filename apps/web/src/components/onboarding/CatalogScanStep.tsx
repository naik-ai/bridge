'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useOnboardingStore } from '@/lib/store/onboarding';
import {
  useDiscoverDatasets,
  useScanDataset,
  useDatasetTables,
} from '@/hooks/use-onboarding';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card } from '@/components/ui/card';
import {
  Loader2,
  AlertCircle,
  ArrowLeft,
  Database,
  Table as TableIcon,
  CheckCircle,
} from 'lucide-react';
import type { Dataset } from '@/types/onboarding';

export function CatalogScanStep() {
  const router = useRouter();
  const { connectionId, setCatalogData, goToPreviousStep, resetOnboarding } =
    useOnboardingStore();

  const discoverMutation = useDiscoverDatasets();
  const scanMutation = useScanDataset();

  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetIds, setSelectedDatasetIds] = useState<Set<string>>(
    new Set()
  );
  const [scannedDatasets, setScannedDatasets] = useState<Set<string>>(new Set());
  const [error, setError] = useState('');
  const [isDiscovering, setIsDiscovering] = useState(false);

  useEffect(() => {
    if (connectionId) {
      handleDiscover();
    }
  }, [connectionId]);

  const handleDiscover = async () => {
    if (!connectionId) return;

    setIsDiscovering(true);
    setError('');

    try {
      const discoveredDatasets = await discoverMutation.mutateAsync(connectionId);
      setDatasets(discoveredDatasets);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to discover datasets');
    } finally {
      setIsDiscovering(false);
    }
  };

  const handleToggleDataset = (datasetId: string) => {
    const newSelected = new Set(selectedDatasetIds);
    if (newSelected.has(datasetId)) {
      newSelected.delete(datasetId);
    } else {
      newSelected.add(datasetId);
    }
    setSelectedDatasetIds(newSelected);
  };

  const handleScanDataset = async (datasetId: string) => {
    setError('');

    try {
      await scanMutation.mutateAsync({ dataset_id: datasetId });
      setScannedDatasets((prev) => new Set(prev).add(datasetId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to scan dataset');
    }
  };

  const handleScanSelected = async () => {
    setError('');

    const datasetIds = Array.from(selectedDatasetIds);
    for (const datasetId of datasetIds) {
      try {
        await scanMutation.mutateAsync({ dataset_id: datasetId });
        setScannedDatasets((prev) => new Set(prev).add(datasetId));
      } catch (err) {
        console.error(`Failed to scan dataset ${datasetId}:`, err);
      }
    }
  };

  const handleFinish = () => {
    setCatalogData({
      selectedDatasets: Array.from(selectedDatasetIds),
    });

    resetOnboarding();
    router.push('/dashboards');
  };

  if (isDiscovering) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Loader2 className="h-12 w-12 animate-spin text-muted-foreground mb-4" />
        <p className="text-muted-foreground">Discovering datasets...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Scan Database Catalog</h2>
        <p className="text-muted-foreground">
          Select datasets to scan and discover tables for dashboard creation.
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {datasets.length === 0 ? (
        <div className="text-center py-12">
          <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground mb-4">No datasets found</p>
          <Button onClick={handleDiscover} variant="outline">
            Retry Discovery
          </Button>
        </div>
      ) : (
        <>
          <div className="space-y-2">
            {datasets.map((dataset) => (
              <DatasetCard
                key={dataset.id}
                dataset={dataset}
                isSelected={selectedDatasetIds.has(dataset.id)}
                isScanned={scannedDatasets.has(dataset.id)}
                onToggle={() => handleToggleDataset(dataset.id)}
                onScan={() => handleScanDataset(dataset.id)}
                isScanning={scanMutation.isPending}
              />
            ))}
          </div>

          <div className="flex justify-between pt-4 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={goToPreviousStep}
              disabled={scanMutation.isPending}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>

            <div className="flex gap-2">
              <Button
                onClick={handleScanSelected}
                disabled={
                  selectedDatasetIds.size === 0 || scanMutation.isPending
                }
                variant="outline"
              >
                {scanMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Scanning...
                  </>
                ) : (
                  `Scan Selected (${selectedDatasetIds.size})`
                )}
              </Button>

              <Button onClick={handleFinish} size="lg">
                Finish Setup
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

interface DatasetCardProps {
  dataset: Dataset;
  isSelected: boolean;
  isScanned: boolean;
  onToggle: () => void;
  onScan: () => void;
  isScanning: boolean;
}

function DatasetCard({
  dataset,
  isSelected,
  isScanned,
  onToggle,
  onScan,
  isScanning,
}: DatasetCardProps) {
  const { data: tables } = useDatasetTables(isScanned ? dataset.id : null);

  return (
    <Card className="p-4">
      <div className="flex items-start gap-4">
        <Checkbox
          checked={isSelected}
          onCheckedChange={onToggle}
          disabled={isScanning}
          className="mt-1"
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <Database className="h-4 w-4 text-muted-foreground flex-shrink-0" />
            <h3 className="font-medium truncate">{dataset.name}</h3>
            {isScanned && (
              <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
            )}
          </div>

          <p className="text-sm text-muted-foreground truncate">
            {dataset.fully_qualified_name}
          </p>

          {dataset.description && (
            <p className="text-sm text-muted-foreground mt-1">
              {dataset.description}
            </p>
          )}

          {isScanned && tables && (
            <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
              <TableIcon className="h-4 w-4" />
              <span>{tables.length} tables discovered</span>
            </div>
          )}
        </div>

        <div className="flex-shrink-0">
          {!isScanned ? (
            <Button
              size="sm"
              variant="outline"
              onClick={onScan}
              disabled={isScanning}
            >
              Scan
            </Button>
          ) : (
            <span className="text-sm text-green-600">Scanned</span>
          )}
        </div>
      </div>
    </Card>
  );
}
