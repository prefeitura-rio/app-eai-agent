'use client';

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/app/utils/utils';
import { Card, CardContent } from '@/components/ui/card';
import { Cpu, Tag } from 'lucide-react';

export interface HistoryItem {
  version_id: string;
  version_number: number;
  created_at: string;
  change_type: 'prompt' | 'config' | 'both';
  is_active: boolean;
  author?: string;
  reason?: string;
  metadata: {
    version_display: string;
  };
  config?: {
    tools?: string[];
    model_name?: string;
  };
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
        return <Badge variant="outline">Prompt</Badge>;
      case 'config':
        return <Badge variant="outline">Config</Badge>;
      case 'both':
        return <Badge variant="outline">Prompt & Config</Badge>;
      default:
        return null;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-CA', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  return (
    <ScrollArea className="h-full">
      <div className="space-y-3 pr-4">
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
              <CardContent className="p-3 space-y-2 text-xs">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    {item.is_active && <Badge variant="success">Ativo</Badge>}
                    {getChangeTypeBadge(item.change_type)}
                  </div>
                </div>
                <div className="space-y-2 pt-1">
                  <div className="flex items-center gap-2 font-semibold">
                    <Tag className="h-4 w-4 text-primary" />
                    <span>{item.metadata.version_display || formatDate(item.created_at) + '-v' + item.version_number.toString()}</span>
                  </div>
                  {item.config?.model_name && (
                     <div className="flex items-center gap-2">
                      <Cpu className="h-4 w-4 text-muted-foreground" />
                      <span className="text-muted-foreground">{item.config.model_name}</span>
                    </div>
                  )}
                </div>
                <hr className="my-2" />
                <div className="text-muted-foreground space-y-1">
                  <p><strong>Autor:</strong> {item.author || 'N/A'}</p>
                  <p><strong>Motivo:</strong> {item.reason || 'N/A'}</p>
                </div>
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
