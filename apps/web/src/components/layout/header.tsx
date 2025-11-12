'use client';

/**
 * Header Component
 *
 * Top navigation with theme toggle and user menu.
 * Uses typed UserInfo from generated API client.
 */

import React from 'react';
import { Moon, Sun, PanelLeft, PanelRight } from 'lucide-react';
import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useSession } from '@/contexts/auth-context';

interface HeaderProps {
  onToggleExplorer: () => void;
  onToggleAssistant: () => void;
  explorerVisible: boolean;
  assistantVisible: boolean;
}

export function Header({
  onToggleExplorer,
  onToggleAssistant,
  explorerVisible,
  assistantVisible,
}: HeaderProps) {
  const { theme, setTheme } = useTheme();
  const { user, logout } = useSession();

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-background px-4">
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleExplorer}
          aria-label="Toggle explorer"
          className="h-8 w-8"
        >
          <PanelLeft className="h-4 w-4" />
        </Button>

        <h1 className="text-lg font-semibold">Peter</h1>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          aria-label="Toggle theme"
          className="h-8 w-8"
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleAssistant}
          aria-label="Toggle assistant"
          className="h-8 w-8"
        >
          <PanelRight className="h-4 w-4" />
        </Button>

        {user && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 px-3">
                <span className="text-sm">{user.email}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col space-y-1">
                  {user.name && <p className="text-sm font-medium">{user.name}</p>}
                  <p className="text-xs text-muted-foreground">{user.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => logout()}>
                <span>Logout</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    </header>
  );
}
