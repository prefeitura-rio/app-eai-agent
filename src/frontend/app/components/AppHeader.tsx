'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import { cn } from '@/app/utils/utils';
import { Moon, Sun} from 'lucide-react';

export interface ActionButton {
  id: string;
  label: string;
  icon: React.ElementType; // Changed to accept a component
  href?: string;
  onClick?: () => void;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
}

interface AppHeaderProps {
  title: string;
  subtitle?: string | null;
  actions: ActionButton[];
  centerTitle?: boolean;
}

export default function AppHeader({ title, subtitle, actions, centerTitle = false }: AppHeaderProps) {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  };

  const allActions = [...actions];

  // Add the theme toggle button dynamically
  if (mounted) {
    allActions.unshift({
      id: 'theme',
      label: `Mudar para tema ${resolvedTheme === 'light' ? 'escuro' : 'claro'}`,
      icon: resolvedTheme === 'dark' ? Sun : Moon,
      onClick: toggleTheme,
    });
  }

  return (
    <header className="w-full border-b bg-background py-6 mb-8">
      <div className="container mx-auto flex flex-wrap items-center justify-between gap-4 px-2 sm:px-4">
        <div
          className={cn(
            'flex min-w-0 flex-grow items-center gap-4',
            centerTitle && 'justify-center'
          )}
        >
          <h1 className="truncate text-2xl font-semibold sm:text-3xl">{title}</h1>
          {subtitle && (
            <small
              className="hidden min-w-0 truncate border-l-2 pl-4 text-base text-muted-foreground sm:block"
              dangerouslySetInnerHTML={{ __html: subtitle }}
            />
          )}
        </div>
        <div className="flex flex-shrink-0 items-center justify-center gap-3">
          {allActions.map(action => {
            const Icon = action.icon;
            const buttonVariant = action.variant || 'outline';

            if (action.href) {
              return (
                <Button key={action.id} variant={buttonVariant} size="icon" asChild>
                  <Link href={action.href} title={action.label}>
                    <Icon className="h-4 w-4" />
                  </Link>
                </Button>
              );
            }
            
            return (
              <Button key={action.id} variant={buttonVariant} size="icon" onClick={action.onClick} title={action.label}>
                <Icon className="h-4 w-4" />
              </Button>
            );
          })}
        </div>
      </div>
    </header>
  );
}