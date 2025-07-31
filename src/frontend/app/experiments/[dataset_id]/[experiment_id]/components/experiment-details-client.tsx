'use client';

import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { ExperimentDetails, ExperimentRun } from '../../../types';
import { useHeader } from '@/app/contexts/HeaderContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from "@/app/utils/utils";
import { downloadFile } from '@/app/utils/csv';
import { FileCode, Download, Bot } from 'lucide-react';
import JsonViewerModal from '@/app/components/JsonViewerModal';
import DownloadLlmJsonModal, { LlmJsonFilters } from './DownloadLlmJsonModal';
import RunDetails from './RunDetails';
import Metadata from './Metadata';
import SummaryMetrics from './SummaryMetrics';
import DetailsPlaceholder from './DetailsPlaceholder';
import Filters from './Filters';

interface ClientProps {
  experimentData: ExperimentDetails;
}

export default function ExperimentDetailsClient({ experimentData }: ClientProps) {
  const { setTitle, setSubtitle, setPageActions } = useHeader();
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [filteredRuns, setFilteredRuns] = useState<ExperimentRun[]>(experimentData.runs);
  const [isJsonModalOpen, setJsonModalOpen] = useState(false);
  const [isLlmModalOpen, setLlmModalOpen] = useState(false);

  const handleDownloadJson = useCallback(() => {
    const jsonString = JSON.stringify(experimentData, null, 2);
    downloadFile(
      `experiment_${experimentData.experiment_name}.json`,
      jsonString,
      'application/json'
    );
  }, [experimentData]);

  const handleDownloadCleanJson = async (numRuns: number | null, filters: LlmJsonFilters): Promise<boolean> => {
    console.log("Downloading clean JSON with", { numRuns, filters });
    
    let runsToExport = [...experimentData.runs];
    
    if (numRuns !== null && numRuns < runsToExport.length) {
        runsToExport.sort(() => 0.5 - Math.random());
        runsToExport = runsToExport.slice(0, numRuns);
    }

    const cleanedRuns = runsToExport.map(run => {
        const cleanRun: any = { id: run.task_data.id };
        if (filters.include_task_data) cleanRun.task_data = run.task_data;
        if (filters.include_evaluations) cleanRun.evaluations = run.evaluations;
        if (filters.include_reasoning_trace) cleanRun.reasoning_trace = run.reasoning_trace;
        return cleanRun;
    });

    downloadFile(
      `experiment_${experimentData.experiment_name}_llm_export.json`,
      JSON.stringify(cleanedRuns, null, 2),
      'application/json'
    );

    return Promise.resolve(true);
  };

  useEffect(() => {
    setTitle(experimentData.experiment_name);
    setSubtitle(`Dataset: ${experimentData.dataset_name}`);
    setPageActions([
        { id: 'download-json', label: 'Baixar JSON', icon: Download, onClick: handleDownloadJson, variant: 'outline' },
        { id: 'download-llm-json', label: 'Exportar LLM', icon: Bot, onClick: () => setLlmModalOpen(true), variant: 'outline' },
        { id: 'view-json', label: 'Ver JSON', icon: FileCode, onClick: () => setJsonModalOpen(true), variant: 'outline' }
    ]);

    return () => setPageActions([]);
  }, [setTitle, setSubtitle, setPageActions, experimentData, handleDownloadJson]);

  const selectedRun = useMemo(() => {
    if (!selectedRunId) return null;
    return filteredRuns.find(run => run.task_data.id === selectedRunId);
  }, [selectedRunId, filteredRuns]);

  const handleFilterChange = (newFilteredRuns: ExperimentRun[]) => {
    setFilteredRuns(newFilteredRuns);
    if (selectedRunId && !newFilteredRuns.some(run => run.task_data.id === selectedRunId)) {
      setSelectedRunId(null);
    }
  };

  return (
    <>
      <JsonViewerModal 
        data={experimentData} 
        open={isJsonModalOpen} 
        onOpenChange={setJsonModalOpen} 
      />
      <DownloadLlmJsonModal
        open={isLlmModalOpen}
        onOpenChange={setLlmModalOpen}
        onConfirm={handleDownloadCleanJson}
      />
      <div className="grid md:grid-cols-[300px_1fr] gap-6 h-full pb-6">
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle>Runs ({filteredRuns.length})</CardTitle>
          </CardHeader>
          <Filters runs={experimentData.runs} onFilterChange={handleFilterChange} />
          <CardContent className="flex-1 overflow-y-auto p-2">
              <div className="space-y-2">
                  {filteredRuns.map((run) => (
                      <div
                          key={run.task_data.id}
                          onClick={() => setSelectedRunId(run.task_data.id)}
                          className={cn(
                              "p-3 rounded-md cursor-pointer border transition-colors",
                              selectedRunId === run.task_data.id
                                  ? "bg-primary text-primary-foreground"
                                  : "hover:bg-muted/ ৫০"
                          )}
                      >
                          <p className="font-semibold text-sm truncate">ID: {run.task_data.id}</p>
                      </div>
                  ))}
              </div>
          </CardContent>
        </Card>

        <div className="overflow-y-auto pr-4">
          <div className="space-y-6">
              <Metadata metadata={experimentData.experiment_metadata} />
              <SummaryMetrics aggregateMetrics={experimentData.aggregate_metrics} />
              {selectedRun ? <RunDetails run={selectedRun} /> : <DetailsPlaceholder />}
          </div>
        </div>
      </div>
    </>
  );
}
