'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/app/utils/utils';

export interface ActionButton {
  id: string;
  label: string;
  icon: React.ElementType;
  href?: string;
  onClick?: () => void;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  iconClassName?: string;
}

interface AppHeaderProps {
  title: string;
  subtitle?: string | null;
  actions?: ActionButton[];
  centerTitle?: boolean;
}

export default function AppHeader({ title, subtitle, actions = [], centerTitle = false }: AppHeaderProps) {
  return (
    <header className="w-full border-b bg-background py-4 mb-6">
      <div className="container mx-auto flex flex-wrap items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <div
          className={cn(
            'flex min-w-0 flex-grow items-center gap-4',
            centerTitle && 'justify-center'
          )}
        >
          <div>
            <h1 className="truncate text-2xl font-semibold sm:text-3xl">{title}</h1>
            {subtitle && (
              <small
                className="hidden min-w-0 truncate text-sm text-muted-foreground sm:block"
                dangerouslySetInnerHTML={{ __html: subtitle }}
              />
            )}
          </div>
        </div>
        <div className="flex flex-shrink-0 items-center justify-center gap-4">
          {actions.map(action => {
            const Icon = action.icon;
            const buttonVariant = action.variant || 'outline';
            
            const buttonContent = (
              <>
                {Icon && <Icon className={cn("h-4 w-4", action.iconClassName)} />}
                <span>{action.label}</span>
              </>
            );

            if (action.href) {
              return (
                <Button key={action.id} variant={buttonVariant} asChild>
                  <Link href={action.href}>{buttonContent}</Link>
                </Button>
              );
            }
            
            return (
              <Button key={action.id} variant={buttonVariant} onClick={action.onClick}>
                {buttonContent}
              </Button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
