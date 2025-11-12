'use client';

import { useState } from 'react';
import { useEditorStore } from '@/lib/store/editor';
import { useDebouncedCallback } from '@/lib/utils/debounce';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';
import { load as parseYAML } from 'js-yaml';
import type { DashboardYAML } from '@/types/dashboard';

export function YAMLEditor() {
  const { yaml, setYamlText, setYaml, setValidationError, validationError } =
    useEditorStore();
  const [localText, setLocalText] = useState(
    yaml ? JSON.stringify(yaml, null, 2) : ''
  );
  const [parseError, setParseError] = useState<string | null>(null);

  const validateYAML = useDebouncedCallback((text: string) => {
    try {
      const parsed = parseYAML(text) as DashboardYAML;
      
      // Basic validation
      if (!parsed.version || typeof parsed.version !== 'number') {
        throw new Error('Missing or invalid version field');
      }
      if (parsed.kind !== 'dashboard') {
        throw new Error('kind must be "dashboard"');
      }
      if (!parsed.slug || typeof parsed.slug !== 'string') {
        throw new Error('Missing or invalid slug field');
      }
      if (!parsed.title || typeof parsed.title !== 'string') {
        throw new Error('Missing or invalid title field');
      }
      if (!Array.isArray(parsed.layout)) {
        throw new Error('layout must be an array');
      }
      if (!Array.isArray(parsed.queries)) {
        throw new Error('queries must be an array');
      }

      setParseError(null);
      setValidationError(null);
      setYaml(parsed, text);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Invalid YAML';
      setParseError(message);
    }
  }, 500);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    setLocalText(text);
    setYamlText(text);
    validateYAML(text);
  };

  return (
    <div className="h-full flex flex-col">
      {(parseError || validationError) && (
        <Alert variant="destructive" className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>
            {parseError ? 'Parse Error' : 'Validation Error'}
          </AlertTitle>
          <AlertDescription>
            {parseError || validationError}
          </AlertDescription>
        </Alert>
      )}

      <Textarea
        value={localText}
        onChange={handleChange}
        className="flex-1 font-mono text-sm resize-none"
        placeholder="Paste YAML content here..."
        spellCheck={false}
      />

      <div className="mt-4 text-xs text-muted-foreground">
        <p>Edit YAML directly. Changes are validated with 500ms debounce.</p>
      </div>
    </div>
  );
}
