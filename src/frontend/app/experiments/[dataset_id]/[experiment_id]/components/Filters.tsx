'use client';

import React, { useState, useMemo } from 'react';
import { Run } from '@/app/components/types';
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";

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

  return (
      <div className="p-4 border-b">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {sortedFilterNames.map(name => (
                  <div key={name} className="grid gap-2">
                      <Label htmlFor={`filter-${name}`}>{name}</Label>
                      <Select
                          value={selectedFilters[name] || 'all'}
                          onValueChange={(value) => handleFilterChange(name, value)}
                      >
                          <SelectTrigger id={`filter-${name}`}>
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
          </div>
          <div className="flex justify-end gap-2 mt-4">
              <Button onClick={applyFilters} size="sm">Aplicar</Button>
              <Button onClick={clearFilters} size="sm" variant="outline">Limpar</Button>
          </div>
      </div>
  );
}
