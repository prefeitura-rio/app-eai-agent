'use client';

import React, { useState, useMemo } from 'react';
import { Run } from '@/app/components/types';
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Badge } from '@/components/ui/badge';

interface FiltersProps {
  runs: Run[];
  onFilterChange: (filteredRuns: Run[]) => void;
}

export default function Filters({ runs, onFilterChange }: FiltersProps) {
  const [selectedFilters, setSelectedFilters] = useState<{ [key: string]: string }>({});

  const filterOptions = useMemo(() => {
      const options: { [key: string]: Set<number> } = {};
      runs.forEach(run => {
          run.annotations?.forEach(ann => {
              if (!options[ann.name]) options[ann.name] = new Set();
              options[ann.name].add(ann.score);
          });
      });
      Object.keys(options).forEach(key => {
          options[key] = new Set(Array.from(options[key]).sort((a, b) => a - b));
      });
      return options;
  }, [runs]);

  const handleFilterChange = (metricName: string, value: string) => {
      setSelectedFilters(prev => ({ ...prev, [metricName]: value }));
  };

  const applyFilters = () => {
      const activeFilters = Object.entries(selectedFilters).filter(([, value]) => value !== 'all' && value !== '');
      
      if (activeFilters.length === 0) {
          onFilterChange(runs);
          return;
      }

      const filtered = runs.filter(run => {
          return activeFilters.every(([metricName, value]) => {
              const annotation = run.annotations?.find(ann => ann.name === metricName);
              return annotation && annotation.score === parseFloat(value);
          });
      });
      onFilterChange(filtered);
  };

  const clearFilters = () => {
      setSelectedFilters({});
      onFilterChange(runs);
  };
  
  const desiredOrder = [
      "Answer Completeness", "Answer Similarity", "Activate Search Tools",
      "Golden Link in Answer", "Golden Link in Tool Calling",
  ];

  const sortedFilterNames = Object.keys(filterOptions).sort((a, b) => {
      const indexA = desiredOrder.indexOf(a);
      const indexB = desiredOrder.indexOf(b);
      if (indexA !== -1 && indexB !== -1) return indexA - indexB;
      if (indexA !== -1) return -1;
      if (indexB !== -1) return 1;
      return a.localeCompare(b);
  });

  const activeFilterCount = Object.values(selectedFilters).filter(value => value !== 'all' && value !== '').length;

  return (
    <Accordion type="single" collapsible className="w-full">
        <AccordionItem value="item-1" className="border-b-0">
            <AccordionTrigger className="p-4 text-base font-semibold hover:no-underline">
                <div className="flex items-center gap-2">
                    Filtros
                    {activeFilterCount > 0 && <Badge>{activeFilterCount}</Badge>}
                </div>
            </AccordionTrigger>
            <AccordionContent className="p-4 pt-0">
                <div className="grid grid-cols-3 gap-x-4 gap-y-2 items-center">
                    {sortedFilterNames.map(name => (
                        <React.Fragment key={name}>
                            <Label htmlFor={`filter-${name}`} className="text-left col-span-2">{name}</Label>
                            <Select
                                value={selectedFilters[name] || 'all'}
                                onValueChange={(value) => handleFilterChange(name, value)}
                            >
                                <SelectTrigger id={`filter-${name}`} className="w-full">
                                    <SelectValue placeholder="Todos" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">Todos</SelectItem>
                                    {Array.from(filterOptions[name]).map(score => (
                                        <SelectItem key={score} value={String(score)}>{score.toFixed(1)}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </React.Fragment>
                    ))}
                    <div className="col-span-3 flex justify-end gap-2 mt-4">
                        <Button onClick={applyFilters} size="sm" className="w-2/3">Aplicar</Button>
                        <Button onClick={clearFilters} size="sm" variant="outline" className="w-1/3">Limpar</Button>
                    </div>
                </div>
            </AccordionContent>
        </AccordionItem>
    </Accordion>
  );
}
