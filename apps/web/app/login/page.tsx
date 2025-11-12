/**
 * Login Page
 *
 * Minimal Google OAuth login interface.
 */

'use client';

import { useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { initiateLogin } from '@/lib/auth';

export default function LoginPage() {
  const searchParams = useSearchParams();
  const returnUrl = searchParams.get('returnUrl') || '/dashboards';

  const handleLogin = () => {
    initiateLogin(returnUrl);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-md space-y-8 px-4">
        <div className="text-center">
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Peter
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Dashboard platform for data exploration
          </p>
        </div>

        <div className="rounded-lg border border-border bg-card p-8">
          <div className="space-y-6">
            <div className="space-y-2 text-center">
              <h2 className="text-2xl font-semibold">Sign in</h2>
              <p className="text-sm text-muted-foreground">
                Continue with your Google account
              </p>
            </div>

            <Button onClick={handleLogin} className="w-full" size="lg">
              Sign in with Google
            </Button>

            <p className="text-center text-xs text-muted-foreground">
              By signing in, you agree to our terms of service
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
