'use client';

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/app/utils/utils';
import { Card, CardContent } from '@/components/ui/card';

export interface HistoryItem {
  version_id: string;
  version_number: number;
  version_display: string;
  created_at: string;
  change_type: 'prompt' | 'config' | 'both';
  is_active: boolean;
  author?: string;
  reason?: string;
  preview?: string;
}

interface VersionHistoryProps {
  history: HistoryItem[];
  onSelectVersion: (version: HistoryItem) => void;
  selectedVersionId?: string | null;
  disabled?: boolean;
}

export default function VersionHistory({ history, onSelectVersion, selectedVersionId, disabled }: VersionHistoryProps) {
  
  const getChangeTypeBadge = (changeType: HistoryItem['change_type']) => {
    switch (changeType) {
      case 'prompt':
        return <Badge variant="secondary">Prompt</Badge>;
      case 'config':
        return <Badge variant="outline">Config</Badge>;
      case 'both':
        return <Badge>Prompt + Config</Badge>;
      default:
        return null;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <ScrollArea className="h-full">
      <div className="space-y-4 pr-6">
        {history.length > 0 ? (
          history.map(item => (
            <Card
              key={item.version_id}
              onClick={() => !disabled && onSelectVersion(item)}
              className={cn(
                "cursor-pointer transition-all duration-200",
                "hover:border-primary/80 hover:shadow-md",
                selectedVersionId === item.version_id && "border-primary bg-muted shadow-md",
                disabled && "cursor-not-allowed opacity-60 hover:border-border hover:shadow-none"
              )}
            >
              <CardContent className="p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="font-semibold text-primary">{item.version_display}</div>
                  {item.is_active && <Badge variant="success">Ativo</Badge>}
                </div>
                <div className="text-xs text-muted-foreground">{formatDate(item.created_at)}</div>
                <div className="flex flex-wrap gap-2">
                  {getChangeTypeBadge(item.change_type)}
                </div>
                <div className="text-xs space-y-1 text-muted-foreground pt-2">
                  {item.author && <p><strong>Autor:</strong> {item.author}</p>}
                  {item.reason && <p><strong>Motivo:</strong> {item.reason}</p>}
                </div>
                {item.preview && (
                  <p className="text-xs mt-2 p-2 bg-background/50 rounded-md whitespace-pre-wrap break-words italic">
                    "{item.preview}"
                  </p>
                )}
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="text-center text-muted-foreground py-16">
            <p>Nenhum histórico disponível para este agente.</p>
          </div>
        )}
      </div>
    </ScrollArea>
  );
}
