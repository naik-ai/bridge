'use client';

import { useOnboardingStore } from '@/lib/store/onboarding';
import { OnboardingLayout } from '@/components/onboarding/OnboardingLayout';
import { TeamCreationStep } from '@/components/onboarding/TeamCreationStep';
import { ConnectionSetupStep } from '@/components/onboarding/ConnectionSetupStep';
import { CatalogScanStep } from '@/components/onboarding/CatalogScanStep';

export default function OnboardingPage() {
  const { currentStep } = useOnboardingStore();

  return (
    <OnboardingLayout>
      {currentStep === 'team' && <TeamCreationStep />}
      {currentStep === 'connection' && <ConnectionSetupStep />}
      {currentStep === 'catalog' && <CatalogScanStep />}
    </OnboardingLayout>
  );
}
