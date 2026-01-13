'use client';

import React from 'react';
import { ExperimentRun } from '../../../types';
import { cn } from "@/app/utils/utils";
import { AlertTriangle } from 'lucide-react';

interface RunsListProps {
  runs: ExperimentRun[];
  selectedRunId: string | null;
  onSelectRun: (runId: string) => void;
}

export default function RunsList({ 
    runs, 
    selectedRunId, 
    onSelectRun,
}: RunsListProps) {
    
    const hasRunError = (run: ExperimentRun) => {
        return run.one_turn_analysis.has_error || run.multi_turn_analysis.has_error;
    };

    return (
        <div className="space-y-2">
            {runs.map((run) => {
                const hasError = hasRunError(run);
                const isSelected = selectedRunId === run.task_data.id;
                
                return (
                    <div
                        key={run.task_data.id}
                        onClick={() => onSelectRun(run.task_data.id)}
                        className={cn(
                            "p-3 rounded-md cursor-pointer border transition-colors",
                            isSelected
                                ? "bg-primary text-primary-foreground border-primary"
                                : "hover:bg-muted/50 border-border",
                            hasError && !isSelected && "border-destructive/50"
                        )}
                    >
                        <div className="flex items-center justify-between">
                            <p className={cn(
                                "font-semibold text-sm truncate",
                                isSelected && "text-primary-foreground"
                            )}>
                                ID: {run.task_data.id}
                            </p>
                            {hasError && (
                                <AlertTriangle className={cn(
                                    "h-4 w-4 flex-shrink-0",
                                    isSelected ? "text-primary-foreground" : "text-destructive"
                                )} />
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
