// src/frontend/app/experiments/types.ts

export interface DatasetInfo {
    dataset_id: string;
    dataset_name: string;
    dataset_description: string;
    num_examples: number;
    num_runs: number;
    created_at: string;
}

export interface DatasetExperimentInfo {
    dataset_id: string;
    experiment_id: string;
    experiment_name: string;
    experiment_description: string;
    experiment_timestamp: string; // Datetime string
    error_summary: Record<string, any>;
    aggregate_metrics: Record<string, any>[];
}

export interface DatasetExample {
    id: string;
    prompt: string;
    [key: string]: any; // Allow other metadata fields
}

export interface DatasetExamplesInfo {
    dataset_id: string;
    num_examples: number;
    examples: DatasetExample[];
}