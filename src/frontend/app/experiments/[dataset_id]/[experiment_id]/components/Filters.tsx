'use client';

import React, { useState, useMemo } from 'react';
import { ExperimentRun } from '../../../types';
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Badge } from '@/components/ui/badge';

interface FiltersProps {
  runs: ExperimentRun[];
  onFilterChange: (filteredRuns: ExperimentRun[]) => void;
}

export default function Filters({ runs, onFilterChange }: FiltersProps) {
  const [selectedFilters, setSelectedFilters] = useState<{ [key: string]: string }>({});

  const filterOptions = useMemo(() => {
      const options: { [key: string]: Set<number> } = {};
      runs.forEach(run => {
          // Aggregate evaluations from both one_turn and multi_turn analysis
          const allEvaluations = [
              ...run.one_turn_analysis.evaluations,
              ...run.multi_turn_analysis.evaluations
          ];

          allEvaluations.forEach(ev => {
              if (ev.score !== null && !ev.has_error) {
                if (!options[ev.metric_name]) options[ev.metric_name] = new Set();
                options[ev.metric_name].add(ev.score);
              }
          });
      });
      // Sort the scores numerically
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
              const allEvaluations = [
                  ...run.one_turn_analysis.evaluations,
                  ...run.multi_turn_analysis.evaluations
              ];
              const evaluation = allEvaluations.find(ev => ev.metric_name === metricName);
              return evaluation && evaluation.score === parseFloat(value);
          });
      });
      onFilterChange(filtered);
  };

  const clearFilters = () => {
      setSelectedFilters({});
      onFilterChange(runs);
  };
  
  const activeFilterCount = Object.values(selectedFilters).filter(value => value !== 'all' && value !== '').length;

  return (
    <Accordion type="single" collapsible className="w-full border-b">
        <AccordionItem value="item-1" className="border-b-0">
            <AccordionTrigger className="p-4 text-base font-semibold hover:no-underline">
                <div className="flex items-center gap-2">
                    Filtros
                    {activeFilterCount > 0 && <Badge>{activeFilterCount}</Badge>}
                </div>
            </AccordionTrigger>
            <AccordionContent className="p-4 pt-0">
                <div className="grid grid-cols-1 gap-y-4">
                    {Object.keys(filterOptions).map(name => (
                        <div key={name} className="space-y-2">
                            <Label htmlFor={`filter-${name}`} className="text-left">{name}</Label>
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
                        </div>
                    ))}
                    <div className="flex justify-end gap-2 mt-4">
                        <Button onClick={applyFilters} size="sm" className="w-2/3">Aplicar</Button>
                        <Button onClick={clearFilters} size="sm" variant="outline" className="w-1/3">Limpar</Button>
                    </div>
                </div>
            </AccordionContent>
        </AccordionItem>
    </Accordion>
  );
}
