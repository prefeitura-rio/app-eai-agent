'use client';

import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { Run, ExperimentData } from '@/app/components/types';
import { useHeader } from '@/app/contexts/HeaderContext';
import JsonViewerModal from '@/app/components/JsonViewerModal';
import DownloadLlmJsonModal, { LlmJsonFilters } from './DownloadLlmJsonModal';
import { downloadFile } from '@/app/utils/csv';
import { Badge } from "@/components/ui/badge";
import {FileCode, Download, Bot} from 'lucide-react';
import Filters from './Filters';
import RunDetails from './RunDetails';
import DetailsPlaceholder from './DetailsPlaceholder';
import Metadata from './Metadata';
import SummaryMetrics from './SummaryMetrics';
import { cn } from "@/app/utils/utils"

const getRunId = (run: Run, index: number) => run.example_id_clean || `run-${index}`;

interface ClientProps {
  initialData: ExperimentData;
  datasetId: string;
  experimentId: string;
  handleDownloadCleanJson: (numExperiments: number | null, filters: LlmJsonFilters) => Promise<boolean>;
}

export default function ExperimentDetailsClient({ initialData, datasetId, experimentId, handleDownloadCleanJson }: ClientProps) {
  const { experiment: runs, experiment_metadata, dataset_name, experiment_name } = initialData;
  const { setTitle, setSubtitle, setPageActions } = useHeader();
  const [isJsonModalOpen, setJsonModalOpen] = useState(false);
  const [isLlmModalOpen, setLlmModalOpen] = useState(false);
  const [filteredRuns, setFilteredRuns] = useState(runs);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  const allTools = useMemo(() => {
    const tools = new Set<string>();
    runs.forEach(run => {
        run.output.agent_output?.ordered?.forEach(step => {
            if (step.type === 'tool_call_message') {
                tools.add(step.message.tool_call.name);
            }
        });
    });
    return Array.from(tools).sort();
  }, [runs]);

  const allMetrics = useMemo(() => {
    const metrics = new Set<string>();
    runs.forEach(run => run.annotations.forEach(ann => metrics.add(ann.name)));
    return Array.from(metrics).sort();
  }, [runs]);

  const handleDownloadJson = useCallback(() => {
    const jsonString = JSON.stringify(initialData, null, 2);
    downloadFile(
      `experiment_${initialData.experiment_name}.json`,
      jsonString,
      'application/json'
    );
  }, [initialData]);

  useEffect(() => {
    setTitle('Detalhes do Experimento');
    const newSubtitle = `${dataset_name || 'Dataset'} <br /> ${experiment_name || 'Experimento'}`;
    setSubtitle(newSubtitle);

    setPageActions([
        { id: 'download-json', label: 'Baixar JSON', icon: Download, onClick: handleDownloadJson },
        { id: 'download-llm-json', label: 'Exportar LLM', icon: Bot, onClick: () => setLlmModalOpen(true) },
        { id: 'view-json', label: 'Ver JSON', icon: FileCode, onClick: () => setJsonModalOpen(true) }
    ]);

    return () => setPageActions([]);
  }, [dataset_name, experiment_name, setTitle, setSubtitle, setPageActions, handleDownloadJson]);
  
  useEffect(() => {
    setFilteredRuns(runs);
  }, [runs]);

  const selectedRun = useMemo(() => {
    if (!selectedRunId) return null;
    return runs.find((run, index) => getRunId(run, index) === selectedRunId);
  }, [runs, selectedRunId]);

  const handleFilterChange = (newFilteredRuns: Run[]) => {
    setFilteredRuns(newFilteredRuns);
    const isSelectedRunVisible = newFilteredRuns.some((run, index) => getRunId(run, index) === selectedRunId);
    if (!isSelectedRunVisible) {
      setSelectedRunId(null);
    }
  };

return (
    <>
      <JsonViewerModal 
        data={initialData} 
        open={isJsonModalOpen} 
        onOpenChange={setJsonModalOpen} 
      />
      <DownloadLlmJsonModal
        open={isLlmModalOpen}
        onOpenChange={setLlmModalOpen}
        onConfirm={handleDownloadCleanJson}
        allTools={allTools}
        allMetrics={allMetrics}
      />
      <div className="grid md:grid-cols-[330px_1fr] gap-4 h-full pb-4">
          <aside className="flex flex-col bg-card border rounded-lg overflow-hidden">
              <Filters runs={runs} onFilterChange={handleFilterChange} />
              <div className="flex justify-between items-center p-4 border-b flex-shrink-0">
                  <h3 className="text-lg font-semibold">Execuções (Runs)</h3>
                  <Badge variant="secondary">{filteredRuns.length}</Badge>
              </div>
              <div className="overflow-y-auto">
                  {filteredRuns.map((run, index) => {
                      const runId = getRunId(run, index);
                      const isActive = selectedRunId === runId;
                      return (
                          <div
                              key={runId}
                              className={cn(
                                'p-2 cursor-pointer border-b transition-colors text-sm',
                                isActive 
                                    ? 'bg-primary text-primary-foreground' 
                                    : 'hover:bg-muted/50'
                              )}
                              onClick={() => setSelectedRunId(runId)}
                          >
                              <span className="font-medium truncate block">ID: {run.output?.metadata?.id || runId}</span>
                              {run.tags && (
                                <div className="flex flex-wrap gap-1 mt-2">
                                    {run.tags.map(tag => (
                                        <Badge key={tag} variant={isActive ? 'secondary' : 'outline'}>{tag}</Badge>
                                    ))}
                                </div>
                              )}
                          </div>
                      );
                  })}
              </div>
          </aside>

          <main className="overflow-y-auto rounded-lg">
              <div className="space-y-6">
                <Metadata metadata={experiment_metadata} />
                <SummaryMetrics runs={runs} />
                {selectedRun ? <RunDetails run={selectedRun} /> : <DetailsPlaceholder />}
              </div>
          </main>
      </div>
    </>
  );
}
