'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useEditorStore } from '@/lib/store/editor';
import { useSaveDashboard } from '@/hooks/use-dashboards';
import { Button } from '@/components/ui/button';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Save, Loader2 } from 'lucide-react';

export function SaveWorkflow() {
  const router = useRouter();
  const { yaml, isDirty, markAsSaved } = useEditorStore();
  const saveMutation = useSaveDashboard();
  const [showConfirm, setShowConfirm] = useState(false);

  const handleSave = async () => {
    if (!yaml) return;

    try {
      await saveMutation.mutateAsync(yaml);
      markAsSaved();
      setShowConfirm(false);
    } catch (error) {
      console.error('Save failed:', error);
    }
  };

  const handleDiscard = () => {
    router.push('/dashboards');
  };

  return (
    <>
      <Button
        onClick={() => setShowConfirm(true)}
        disabled={!isDirty || saveMutation.isPending}
        size="sm"
      >
        {saveMutation.isPending ? (
          <>
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            Saving...
          </>
        ) : (
          <>
            <Save className="h-4 w-4 mr-2" />
            Save
          </>
        )}
      </Button>

      <AlertDialog open={showConfirm} onOpenChange={setShowConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Save Changes?</AlertDialogTitle>
            <AlertDialogDescription>
              You have unsaved changes to {yaml?.title}. Do you want to save
              them before leaving?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={handleDiscard}>
              Discard
            </AlertDialogCancel>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleSave}>
              Save Changes
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
