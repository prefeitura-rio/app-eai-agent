'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Settings2, Eye, EyeOff } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface MetricsSelectorProps {
  availableMetrics: string[];
  selectedMetrics: string[];
  onSelectionChange: (metrics: string[]) => void;
  storageKey?: string;
}

export default function MetricsSelector({
  availableMetrics,
  selectedMetrics,
  onSelectionChange,
  storageKey = 'experiment-visible-metrics',
}: MetricsSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          // Only use saved metrics that still exist in available metrics
          const validMetrics = parsed.filter((m: string) => availableMetrics.includes(m));
          if (validMetrics.length > 0) {
            onSelectionChange(validMetrics);
          }
        } catch {
          // Ignore parse errors
        }
      }
    }
  }, [availableMetrics, storageKey]); // eslint-disable-line react-hooks/exhaustive-deps

  // Save to localStorage when selection changes
  useEffect(() => {
    if (typeof window !== 'undefined' && selectedMetrics.length > 0) {
      localStorage.setItem(storageKey, JSON.stringify(selectedMetrics));
    }
  }, [selectedMetrics, storageKey]);

  const handleToggleMetric = (metric: string) => {
    if (selectedMetrics.includes(metric)) {
      onSelectionChange(selectedMetrics.filter(m => m !== metric));
    } else {
      onSelectionChange([...selectedMetrics, metric]);
    }
  };

  const handleSelectAll = () => {
    onSelectionChange([...availableMetrics]);
  };

  const handleSelectNone = () => {
    onSelectionChange([]);
  };

  const hiddenCount = availableMetrics.length - selectedMetrics.length;

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Settings2 className="h-4 w-4" />
          <span>Colunas</span>
          {hiddenCount > 0 && (
            <Badge variant="secondary" className="ml-1">
              {hiddenCount} ocultas
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80" align="end">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-sm">Métricas Visíveis</h4>
            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSelectAll}
                className="h-7 px-2 text-xs"
              >
                <Eye className="h-3 w-3 mr-1" />
                Todas
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSelectNone}
                className="h-7 px-2 text-xs"
              >
                <EyeOff className="h-3 w-3 mr-1" />
                Nenhuma
              </Button>
            </div>
          </div>
          
          <div className="max-h-64 overflow-y-auto space-y-2">
            {availableMetrics.map((metric) => (
              <div key={metric} className="flex items-center space-x-2">
                <Checkbox
                  id={`metric-${metric}`}
                  checked={selectedMetrics.includes(metric)}
                  onCheckedChange={() => handleToggleMetric(metric)}
                />
                <Label
                  htmlFor={`metric-${metric}`}
                  className="text-sm font-normal cursor-pointer flex-1 truncate"
                  title={metric}
                >
                  {metric}
                </Label>
              </div>
            ))}
          </div>
          
          <div className="text-xs text-muted-foreground pt-2 border-t">
            {selectedMetrics.length} de {availableMetrics.length} métricas visíveis
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
