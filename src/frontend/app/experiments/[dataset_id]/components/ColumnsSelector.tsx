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

interface ColumnsSelectorProps {
  availableColumns: string[];
  selectedColumns: string[];
  onSelectionChange: (columns: string[]) => void;
  storageKey?: string;
}

export default function ColumnsSelector({
  availableColumns,
  selectedColumns,
  onSelectionChange,
  storageKey = 'dataset-experiments-visible-columns',
}: ColumnsSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined' && availableColumns.length > 0) {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          // Only use saved columns that still exist
          const validColumns = parsed.filter((c: string) => availableColumns.includes(c));
          if (validColumns.length > 0) {
            onSelectionChange(validColumns);
          }
        } catch {
          // Ignore parse errors
        }
      }
    }
  }, [availableColumns, storageKey]); // eslint-disable-line react-hooks/exhaustive-deps

  // Save to localStorage when selection changes
  useEffect(() => {
    if (typeof window !== 'undefined' && selectedColumns.length > 0) {
      localStorage.setItem(storageKey, JSON.stringify(selectedColumns));
    }
  }, [selectedColumns, storageKey]);

  const handleToggleColumn = (column: string) => {
    if (selectedColumns.includes(column)) {
      onSelectionChange(selectedColumns.filter(c => c !== column));
    } else {
      onSelectionChange([...selectedColumns, column]);
    }
  };

  const handleSelectAll = () => {
    onSelectionChange([...availableColumns]);
  };

  const handleSelectNone = () => {
    onSelectionChange([]);
  };

  const hiddenCount = availableColumns.length - selectedColumns.length;

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
            {availableColumns.map((column) => (
              <div key={column} className="flex items-center space-x-2">
                <Checkbox
                  id={`column-${column}`}
                  checked={selectedColumns.includes(column)}
                  onCheckedChange={() => handleToggleColumn(column)}
                />
                <Label
                  htmlFor={`column-${column}`}
                  className="text-sm font-normal cursor-pointer flex-1 truncate"
                  title={column}
                >
                  {column}
                </Label>
              </div>
            ))}
          </div>
          
          <div className="text-xs text-muted-foreground pt-2 border-t">
            {selectedColumns.length} de {availableColumns.length} métricas visíveis
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
