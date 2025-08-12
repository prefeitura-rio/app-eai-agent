'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Download, Loader2, CheckCircle, XCircle } from 'lucide-react';

// Simplified filters for the new data structure
export interface LlmJsonFilters {
  include_task_data: boolean;
  include_evaluations: boolean;
  include_reasoning_trace: boolean;
}

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (numRuns: number | null, filters: LlmJsonFilters) => Promise<boolean>;
}

const initialFiltersState: LlmJsonFilters = {
    include_task_data: true,
    include_evaluations: true,
    include_reasoning_trace: true,
};

type DownloadStatus = 'idle' | 'loading' | 'success' | 'error';

export default function DownloadLlmJsonModal({ open, onOpenChange, onConfirm }: Props) {
  const [numRuns, setNumRuns] = useState<number | null>(null);
  const [filters, setFilters] = useState<LlmJsonFilters>(initialFiltersState);
  const [status, setStatus] = useState<DownloadStatus>('idle');

  useEffect(() => {
    if (open) {
      setStatus('idle');
      setFilters(initialFiltersState);
    }
  }, [open]);

  const handleConfirm = async () => {
    setStatus('loading');
    const success = await onConfirm(numRuns, filters);
    setStatus(success ? 'success' : 'error');
  };

  const isLoading = status === 'loading';

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Exportar Runs para Análise LLM</DialogTitle>
        </DialogHeader>
        
        <div className="h-6">
            {status === 'success' && <div className="flex items-center text-success text-sm"><CheckCircle className="h-4 w-4 mr-2"/><span>Download iniciado.</span></div>}
            {status === 'error' && <div className="flex items-center text-destructive text-sm"><XCircle className="h-4 w-4 mr-2"/><span>Falha no download. Tente novamente.</span></div>}
        </div>

        <ScrollArea className="max-h-[60vh] p-4 border rounded-md">
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="num-runs">Número de Runs (opcional)</Label>
              <Input
                id="num-runs"
                type="number"
                placeholder="Deixe em branco para exportar todos"
                onChange={(e) => setNumRuns(e.target.value ? parseInt(e.target.value) : null)}
                disabled={isLoading}
              />
              <p className="text-sm text-muted-foreground">
                Selecione uma amostra aleatória de runs para exportar.
              </p>
            </div>

            <Card>
              <CardHeader><CardTitle>Conteúdo a Incluir</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-2">
                    <Checkbox id="task-data" checked={filters.include_task_data} onCheckedChange={(checked) => setFilters(f => ({ ...f, include_task_data: !!checked }))} disabled={isLoading} />
                    <Label htmlFor="task-data">Dados da Tarefa (Input)</Label>
                </div>
                <div className="flex items-center space-x-2">
                    <Checkbox id="evaluations" checked={filters.include_evaluations} onCheckedChange={(checked) => setFilters(f => ({ ...f, include_evaluations: !!checked }))} disabled={isLoading} />
                    <Label htmlFor="evaluations">Avaliações (Juiz)</Label>
                </div>
                <div className="flex items-center space-x-2">
                    <Checkbox id="reasoning-trace" checked={filters.include_reasoning_trace} onCheckedChange={(checked) => setFilters(f => ({ ...f, include_reasoning_trace: !!checked }))} disabled={isLoading} />
                    <Label htmlFor="reasoning-trace">Cadeia de Pensamento</Label>
                </div>
              </CardContent>
            </Card>
          </div>
        </ScrollArea>
        <DialogFooter>
            <Button variant="outline" onClick={() => onOpenChange(false)}>
                {status === 'success' ? 'Fechar' : 'Cancelar'}
            </Button>
            <Button onClick={handleConfirm} disabled={isLoading}>
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {status === 'loading' && 'Exportando...'}
                {status === 'idle' && <><Download className="mr-2 h-4 w-4" /> Exportar JSON</>}
                {status === 'error' && <><Download className="mr-2 h-4 w-4" /> Tentar Novamente</>}
                {status === 'success' && <><Download className="mr-2 h-4 w-4" /> Exportar Novamente</>}
            </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
