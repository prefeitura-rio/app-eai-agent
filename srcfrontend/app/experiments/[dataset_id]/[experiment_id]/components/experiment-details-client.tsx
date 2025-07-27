'use client';

import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { marked } from 'marked';
import { Run, Annotation, OrderedStep, ExperimentMetadata } from '@/app/components/types';
import { useHeader } from '@/app/contexts/HeaderContext';
import JsonViewerModal from '@/app/components/JsonViewerModal';
import { downloadFile } from '@/app/utils/csv';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Lightbulb, Wrench, LogIn, MessageSquare, BarChart, List, FileCode, Download } from 'lucide-react';

// NOTE: All sub-components (Filters, Metadata, SummaryMetrics, etc.) are assumed to be defined here as they were before.
// This rewrite focuses on restoring the main component's JSX.

const getRunId = (run: Run, index: number) => run.example_id_clean || `run-${index}`;

// ... (Keep all sub-components like Filters, Metadata, SummaryMetrics, Evaluations, ReasoningTimeline, Comparison, RunDetails, DetailsPlaceholder here)

export default function ExperimentDetailsClient({ initialData }: { initialData: { experiment: Run[], experiment_metadata: ExperimentMetadata | null, dataset_name: string, experiment_name: string } }) {
    const { experiment: runs, experiment_metadata, dataset_name, experiment_name } = initialData;
    const { setTitle, setSubtitle, setPageActions } = useHeader();
    const [isJsonModalOpen, setJsonModalOpen] = useState(false);

    const [filteredRuns, setFilteredRuns] = useState(runs);
    const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

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
            {isJsonModalOpen && (
                <JsonViewerModal data={initialData}>
                    {/* The trigger is now part of the page actions, so we don't need a visible trigger here */}
                </JsonViewerModal>
            )}
            <div className="grid md:grid-cols-[350px_1fr] gap-4 p-4 h-full">
                <aside className="flex flex-col bg-card border rounded-lg">
                    <Filters runs={runs} onFilterChange={handleFilterChange} />
                    <div className="flex justify-between items-center p-4 border-b">
                        <h3 className="text-lg font-semibold">Execuções (Runs)</h3>
                        <Badge variant="secondary">{filteredRuns.length}</Badge>
                    </div>
                    <div className="overflow-y-auto">
                        {filteredRuns.map((run, index) => {
                            const runId = getRunId(run, index);
                            return (
                                <div
                                    key={runId}
                                    className={`p-3 cursor-pointer border-b ${selectedRunId === runId ? 'bg-accent text-accent-foreground' : 'hover:bg-muted/50'}`}
                                    onClick={() => setSelectedRunId(runId)}
                                >
                                    <span className="font-medium truncate">ID: {run.output?.metadata?.id || runId}</span>
                                </div>
                            );
                        })}
                    </div>
                </aside>

                <main className="overflow-y-auto bg-card border rounded-lg p-6">
                    <Metadata metadata={experiment_metadata} />
                    <SummaryMetrics runs={runs} />
                    {selectedRun ? <RunDetails run={selectedRun} /> : <DetailsPlaceholder />}
                </main>
            </div>
        </>
    );
}
