'use client';

import React, { useState, useMemo, useEffect } from 'react';
import { ExperimentDetails } from '../../../types';
import { useHeader } from '@/app/contexts/HeaderContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from "@/app/utils/utils";
import RunDetails from './RunDetails';
import Metadata from './Metadata';
import SummaryMetrics from './SummaryMetrics';
import DetailsPlaceholder from './DetailsPlaceholder';

interface ClientProps {
  experimentData: ExperimentDetails;
}

export default function ExperimentDetailsClient({ experimentData }: ClientProps) {
  const { setTitle, setSubtitle } = useHeader();
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  useEffect(() => {
    setTitle(experimentData.experiment_name);
    setSubtitle(`Dataset: ${experimentData.dataset_name}`);
  }, [setTitle, setSubtitle, experimentData]);

  const selectedRun = useMemo(() => {
    if (!selectedRunId) return null;
    return experimentData.runs.find(run => run.task_data.id === selectedRunId);
  }, [selectedRunId, experimentData.runs]);

  return (
    <div className="grid md:grid-cols-[300px_1fr] gap-6 h-full pb-6">
      {/* Sidebar com a lista de Runs */}
      <Card className="flex flex-col">
        <CardHeader>
          <CardTitle>Runs ({experimentData.runs.length})</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto p-2">
            <div className="space-y-2">
                {experimentData.runs.map((run) => (
                    <div
                        key={run.task_data.id}
                        onClick={() => setSelectedRunId(run.task_data.id)}
                        className={cn(
                            "p-3 rounded-md cursor-pointer border transition-colors",
                            selectedRunId === run.task_data.id
                                ? "bg-primary text-primary-foreground"
                                : "hover:bg-muted/50"
                        )}
                    >
                        <p className="font-semibold text-sm truncate">ID: {run.task_data.id}</p>
                    </div>
                ))}
            </div>
        </CardContent>
      </Card>

      {/* Conteúdo Principal */}
      <div className="overflow-y-auto pr-4">
        <div className="space-y-6">
            <Metadata metadata={experimentData.experiment_metadata} />
            <SummaryMetrics aggregateMetrics={experimentData.aggregate_metrics} />
            {selectedRun ? <RunDetails run={selectedRun} /> : <DetailsPlaceholder />}
        </div>
      </div>
    </div>
  );
}
