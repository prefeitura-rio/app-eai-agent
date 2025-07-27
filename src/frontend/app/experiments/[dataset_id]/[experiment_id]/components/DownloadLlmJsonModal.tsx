'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Download } from 'lucide-react';

export interface LlmJsonFilters {
  basic_fields: string[];
  reasoning_messages: { include: boolean };
  tool_call_messages: { include: boolean; selected_tools: string[] | null };
  tool_return_messages: {
    include: boolean;
    selected_tools: string[] | null;
    selected_content: string[] | null;
  };
  metrics: { include: boolean; selected_metrics: string[] | null };
}

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (numExperiments: number | null, filters: LlmJsonFilters) => void;
  allTools: string[];
  allMetrics: string[];
}

const initialFiltersState: LlmJsonFilters = {
    basic_fields: ['message_id', 'menssagem', 'golden_answer', 'model_response'],
    reasoning_messages: { include: true },
    tool_call_messages: { include: true, selected_tools: [] },
    tool_return_messages: {
      include: true,
      selected_tools: [],
      selected_content: ['text', 'sources', 'web_search_queries'],
    },
    metrics: { include: true, selected_metrics: [] },
};

export default function DownloadLlmJsonModal({ open, onOpenChange, onConfirm, allTools, allMetrics }: Props) {
  const [numExperiments, setNumExperiments] = useState<number | null>(null);
  const [filters, setFilters] = useState<LlmJsonFilters>(initialFiltersState);

  useEffect(() => {
    if (open) {
      setFilters({
        ...initialFiltersState,
        tool_call_messages: { ...initialFiltersState.tool_call_messages, selected_tools: allTools },
        tool_return_messages: { ...initialFiltersState.tool_return_messages, selected_tools: allTools },
        metrics: { ...initialFiltersState.metrics, selected_metrics: allMetrics },
      });
    }
  }, [open, allTools, allMetrics]);

  const handleConfirm = () => {
    onConfirm(numExperiments, filters);
    onOpenChange(false);
  };

  const handleSelectAll = () => {
    setFilters({
      basic_fields: ['message_id', 'menssagem', 'golden_answer', 'model_response'],
      reasoning_messages: { include: true },
      tool_call_messages: { include: true, selected_tools: allTools },
      tool_return_messages: {
        include: true,
        selected_tools: allTools,
        selected_content: ['text', 'sources', 'web_search_queries'],
      },
      metrics: { include: true, selected_metrics: allMetrics },
    });
  };

  const handleDeselectAll = () => {
    setFilters({
      basic_fields: [],
      reasoning_messages: { include: false },
      tool_call_messages: { include: false, selected_tools: [] },
      tool_return_messages: {
        include: false,
        selected_tools: [],
        selected_content: [],
      },
      metrics: { include: false, selected_metrics: [] },
    });
  };

  const CheckboxGroup = ({ items, selectedItems, onSelectionChange, disabled = false }: { items: string[], selectedItems: string[] | null, onSelectionChange: (newSelection: string[]) => void, disabled?: boolean }) => (
    <div className="grid grid-cols-2 gap-2 mt-2">
      {items.map((item: string) => (
        <div key={item} className="flex items-center space-x-2">
          <Checkbox
            id={`${item}`}
            checked={selectedItems?.includes(item)}
            onCheckedChange={(checked) => {
              const newSelection = checked
                ? [...(selectedItems || []), item]
                : (selectedItems || []).filter((i: string) => i !== item);
              onSelectionChange(newSelection);
            }}
            disabled={disabled}
          />
          <Label htmlFor={`${item}`} className={disabled ? 'text-muted-foreground' : ''}>{item}</Label>
        </div>
      ))}
    </div>
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Download JSON for LLM</DialogTitle>
        </DialogHeader>
        <ScrollArea className="max-h-[70vh] p-4 border rounded-md">
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="num-experiments">Número de experimentos (opcional)</Label>
              <Input
                id="num-experiments"
                type="number"
                placeholder="Deixe em branco para baixar todos"
                onChange={(e) => setNumExperiments(e.target.value ? parseInt(e.target.value) : null)}
              />
              <p className="text-sm text-muted-foreground">
                Realiza o download de uma versão mais limpa dos dados do experimento. Se não especificar um número, todos os experimentos serão baixados. Se especificar, será feita uma seleção aleatória.
              </p>
            </div>

            <div className="flex space-x-2">
                <Button variant="outline" size="sm" onClick={handleSelectAll}>Selecionar Todos</Button>
                <Button variant="outline" size="sm" onClick={handleDeselectAll}>Limpar Seleção</Button>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Campos Básicos</CardTitle>
              </CardHeader>
              <CardContent>
                <CheckboxGroup
                  items={['message_id', 'menssagem', 'golden_answer', 'model_response']}
                  selectedItems={filters.basic_fields}
                  onSelectionChange={(newSelection: string[]) => setFilters(f => ({ ...f, basic_fields: newSelection }))}
                />
              </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <div className="flex items-center space-x-2">
                        <Checkbox
                            id="reasoning-messages"
                            checked={filters.reasoning_messages.include}
                            onCheckedChange={(checked) => setFilters(f => ({ ...f, reasoning_messages: { include: !!checked } }))}
                        />
                        <Label htmlFor="reasoning-messages" className="text-base font-semibold">Mensagens de Raciocínio</Label>
                    </div>
                </CardHeader>
            </Card>

            <Card>
                <CardHeader>
                     <div className="flex items-center space-x-2">
                        <Checkbox
                            id="tool-calls"
                            checked={filters.tool_call_messages.include}
                            onCheckedChange={(checked) => setFilters(f => ({ ...f, tool_call_messages: { ...f.tool_call_messages, include: !!checked } }))}
                        />
                        <Label htmlFor="tool-calls" className="text-base font-semibold">Chamadas de Ferramentas</Label>
                    </div>
                </CardHeader>
                <CardContent>
                    <CheckboxGroup
                        items={allTools}
                        selectedItems={filters.tool_call_messages.selected_tools}
                        onSelectionChange={(newSelection: string[]) => setFilters(f => ({ ...f, tool_call_messages: { ...f.tool_call_messages, selected_tools: newSelection } }))}
                        disabled={!filters.tool_call_messages.include}
                    />
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <div className="flex items-center space-x-2">
                        <Checkbox
                            id="tool-returns"
                            checked={filters.tool_return_messages.include}
                            onCheckedChange={(checked) => setFilters(f => ({ ...f, tool_return_messages: { ...f.tool_return_messages, include: !!checked } }))}
                        />
                        <Label htmlFor="tool-returns" className="text-base font-semibold">Retornos de Ferramentas</Label>
                    </div>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <h4 className="font-semibold text-sm mb-2">Ferramentas</h4>
                        <CheckboxGroup
                            items={allTools}
                            selectedItems={filters.tool_return_messages.selected_tools}
                            onSelectionChange={(newSelection: string[]) => setFilters(f => ({ ...f, tool_return_messages: { ...f.tool_return_messages, selected_tools: newSelection } }))}
                            disabled={!filters.tool_return_messages.include}
                        />
                    </div>
                    <div>
                        <h4 className="font-semibold text-sm mb-2">Conteúdo</h4>
                        <CheckboxGroup
                            items={['text', 'sources', 'web_search_queries']}
                            selectedItems={filters.tool_return_messages.selected_content}
                            onSelectionChange={(newSelection: string[]) => setFilters(f => ({ ...f, tool_return_messages: { ...f.tool_return_messages, selected_content: newSelection } }))}
                            disabled={!filters.tool_return_messages.include}
                        />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <div className="flex items-center space-x-2">
                        <Checkbox
                            id="metrics"
                            checked={filters.metrics.include}
                            onCheckedChange={(checked) => setFilters(f => ({ ...f, metrics: { ...f.metrics, include: !!checked } }))}
                        />
                        <Label htmlFor="metrics" className="text-base font-semibold">Métricas</Label>
                    </div>
                </CardHeader>
                <CardContent>
                    <CheckboxGroup
                        items={allMetrics}
                        selectedItems={filters.metrics.selected_metrics}
                        onSelectionChange={(newSelection: string[]) => setFilters(f => ({ ...f, metrics: { ...f.metrics, selected_metrics: newSelection } }))}
                        disabled={!filters.metrics.include}
                    />
                </CardContent>
            </Card>

          </div>
        </ScrollArea>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancelar</Button>
          </DialogClose>
          <Button onClick={handleConfirm}>
            <Download className="mr-2 h-4 w-4" />
            Baixar JSON
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
