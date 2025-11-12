'use client';

import { useOnboardingStore } from '@/lib/store/onboarding';
import { Card } from '@/components/ui/card';
import { Check } from 'lucide-react';

interface OnboardingLayoutProps {
  children: React.ReactNode;
}

export function OnboardingLayout({ children }: OnboardingLayoutProps) {
  const { currentStep, teamCompleted, connectionCompleted, catalogCompleted } =
    useOnboardingStore();

  const steps = [
    { id: 'team', label: 'Create Team', completed: teamCompleted },
    { id: 'connection', label: 'Setup Connection', completed: connectionCompleted },
    { id: 'catalog', label: 'Scan Catalog', completed: catalogCompleted },
  ];

  return (
    <div className="min-h-screen bg-secondary/20">
      <div className="max-w-4xl mx-auto py-12 px-4">
        {/* Progress Steps */}
        <div className="mb-12">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center">
                  <div
                    className={`
                      w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors
                      ${
                        step.completed
                          ? 'bg-foreground border-foreground text-background'
                          : currentStep === step.id
                          ? 'border-foreground text-foreground'
                          : 'border-border text-muted-foreground'
                      }
                    `}
                  >
                    {step.completed ? (
                      <Check className="h-5 w-5" />
                    ) : (
                      <span className="text-sm font-semibold">{index + 1}</span>
                    )}
                  </div>
                  <span
                    className={`
                      mt-2 text-sm font-medium
                      ${
                        currentStep === step.id
                          ? 'text-foreground'
                          : 'text-muted-foreground'
                      }
                    `}
                  >
                    {step.label}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`
                      flex-1 h-0.5 mx-4
                      ${step.completed ? 'bg-foreground' : 'bg-border'}
                    `}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Content */}
        <Card className="p-8">{children}</Card>
      </div>
    </div>
  );
}
