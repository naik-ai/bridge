'use client';

import { useState } from 'react';
import { useOnboardingStore } from '@/lib/store/onboarding';
import { useCreateConnection, useTestConnection } from '@/hooks/use-onboarding';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, AlertCircle, ArrowLeft, CheckCircle } from 'lucide-react';
import type { ConnectionType } from '@/types/onboarding';

export function ConnectionSetupStep() {
  const { teamId, setConnectionData, goToNextStep, goToPreviousStep } =
    useOnboardingStore();
  const createConnectionMutation = useCreateConnection();
  const testConnectionMutation = useTestConnection();

  const [connectionType, setConnectionType] =
    useState<ConnectionType>('bigquery');
  const [name, setName] = useState('');
  const [credentialsJson, setCredentialsJson] = useState('');
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [testStatus, setTestStatus] = useState<
    'idle' | 'testing' | 'success' | 'failed'
  >('idle');

  const handleTestConnection = async () => {
    if (!connectionId) return;

    setTestStatus('testing');
    setError('');

    try {
      const result = await testConnectionMutation.mutateAsync(connectionId);
      if (result.status === 'active') {
        setTestStatus('success');
      } else {
        setTestStatus('failed');
        setError('Connection test failed. Please check your credentials.');
      }
    } catch (err) {
      setTestStatus('failed');
      setError(err instanceof Error ? err.message : 'Connection test failed');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!name.trim()) {
      setError('Connection name is required');
      return;
    }

    if (!credentialsJson.trim()) {
      setError('Credentials are required');
      return;
    }

    let credentials;
    try {
      credentials = JSON.parse(credentialsJson);
    } catch {
      setError('Invalid JSON format for credentials');
      return;
    }

    if (!teamId) {
      setError('Team ID not found. Please go back and create a team first.');
      return;
    }

    try {
      const connection = await createConnectionMutation.mutateAsync({
        team_id: teamId,
        name,
        connection_type: connectionType,
        credentials,
      });

      setConnectionId(connection.id);
      setConnectionData(
        {
          name,
          connectionType,
          credentials,
        },
        connection.id
      );

      // Auto-test after creation
      setTestStatus('testing');
      const testResult = await testConnectionMutation.mutateAsync(connection.id);
      if (testResult.status === 'active') {
        setTestStatus('success');
      } else {
        setTestStatus('failed');
        setError('Connection created but test failed. You can retry the test.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create connection');
    }
  };

  const handleContinue = () => {
    if (testStatus === 'success') {
      goToNextStep();
    } else {
      setError('Please test the connection successfully before continuing');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Setup Database Connection</h2>
        <p className="text-muted-foreground">
          Connect to your data warehouse to enable dashboard creation.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label>Database Type</Label>
          <Tabs
            value={connectionType}
            onValueChange={(value) => setConnectionType(value as ConnectionType)}
          >
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="bigquery">BigQuery</TabsTrigger>
              <TabsTrigger value="postgres">PostgreSQL</TabsTrigger>
              <TabsTrigger value="snowflake">Snowflake</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <div className="space-y-2">
          <Label htmlFor="connection-name">Connection Name</Label>
          <Input
            id="connection-name"
            placeholder="Production BigQuery"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={createConnectionMutation.isPending || !!connectionId}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="credentials">
            Credentials (JSON)
            {connectionType === 'bigquery' && (
              <span className="ml-2 text-sm text-muted-foreground">
                Service account key file
              </span>
            )}
          </Label>
          <Textarea
            id="credentials"
            placeholder='{"type": "service_account", "project_id": "...", ...}'
            value={credentialsJson}
            onChange={(e) => setCredentialsJson(e.target.value)}
            disabled={createConnectionMutation.isPending || !!connectionId}
            rows={8}
            className="font-mono text-sm"
          />
          <p className="text-sm text-muted-foreground">
            Paste your service account JSON or connection credentials here
          </p>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {testStatus === 'success' && (
          <Alert className="border-green-600 text-green-600">
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>Connection test successful!</AlertDescription>
          </Alert>
        )}

        <div className="flex justify-between pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={goToPreviousStep}
            disabled={createConnectionMutation.isPending}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>

          <div className="flex gap-2">
            {!connectionId ? (
              <Button
                type="submit"
                disabled={createConnectionMutation.isPending || !name || !credentialsJson}
                size="lg"
              >
                {createConnectionMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create & Test Connection'
                )}
              </Button>
            ) : (
              <>
                {testStatus !== 'success' && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleTestConnection}
                    disabled={testConnectionMutation.isPending}
                  >
                    {testConnectionMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Testing...
                      </>
                    ) : (
                      'Retry Test'
                    )}
                  </Button>
                )}
                <Button
                  type="button"
                  onClick={handleContinue}
                  disabled={testStatus !== 'success'}
                  size="lg"
                >
                  Continue
                </Button>
              </>
            )}
          </div>
        </div>
      </form>
    </div>
  );
}
