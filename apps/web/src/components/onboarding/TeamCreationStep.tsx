'use client';

import { useState } from 'react';
import { useOnboardingStore } from '@/lib/store/onboarding';
import { useCreateTeam } from '@/hooks/use-onboarding';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, AlertCircle } from 'lucide-react';

export function TeamCreationStep() {
  const { setTeamData, goToNextStep } = useOnboardingStore();
  const createTeamMutation = useCreateTeam();

  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [error, setError] = useState('');

  const generateSlug = (teamName: string) => {
    return teamName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  };

  const handleNameChange = (value: string) => {
    setName(value);
    if (!slug) {
      setSlug(generateSlug(value));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!name.trim()) {
      setError('Team name is required');
      return;
    }

    if (!slug.trim()) {
      setError('Team slug is required');
      return;
    }

    if (!/^[a-z0-9-]+$/.test(slug)) {
      setError('Slug must contain only lowercase letters, numbers, and hyphens');
      return;
    }

    try {
      const team = await createTeamMutation.mutateAsync({ name, slug });
      setTeamData({ name, slug }, team.id);
      goToNextStep();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create team');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Create Your Team</h2>
        <p className="text-muted-foreground">
          Let's start by setting up your team workspace.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="team-name">Team Name</Label>
          <Input
            id="team-name"
            placeholder="My Analytics Team"
            value={name}
            onChange={(e) => handleNameChange(e.target.value)}
            disabled={createTeamMutation.isPending}
          />
          <p className="text-sm text-muted-foreground">
            The display name for your team
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="team-slug">Team Slug</Label>
          <Input
            id="team-slug"
            placeholder="my-analytics-team"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            disabled={createTeamMutation.isPending}
          />
          <p className="text-sm text-muted-foreground">
            Used in URLs. Lowercase letters, numbers, and hyphens only.
          </p>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="flex justify-end pt-4">
          <Button
            type="submit"
            disabled={createTeamMutation.isPending || !name || !slug}
            size="lg"
          >
            {createTeamMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating Team...
              </>
            ) : (
              'Continue'
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
