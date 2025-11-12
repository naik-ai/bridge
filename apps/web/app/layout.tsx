/**
 * Root Layout
 *
 * Wraps entire app with providers and sets up fonts.
 */

import type { Metadata } from 'next';
import '@fontsource-variable/inter';
import './globals.css';
import { Providers } from '@/components/providers';

export const metadata: Metadata = {
  title: 'Peter - Dashboard Platform',
  description: 'Data exploration and dashboard authoring',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
