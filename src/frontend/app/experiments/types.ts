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
    execution_summary: {
        total_duration_seconds: number;
        [key: string]: any;
    };
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

export interface ExperimentRun {
    duration_seconds: number;
    task_data: Record<string, any>;
    agent_response: {
        one_turn: string | null;
        multi_turn_final: string | null;
    };
    reasoning_trace: {
        one_turn: Record<string, any>[] | null;
        multi_turn: Record<string, any>[] | null;
    };
    evaluations: {
        metric_name: string;
        score: number | null;
        judge_annotations: string | null;
        [key: string]: any;
    }[];
    [key: string]: any;
}

export interface ExperimentDetails {
    dataset_id: string;
    dataset_name: string;
    dataset_description: string;
    experiment_id: string;
    experiment_name: string;
    experiment_description: string;
    experiment_timestamp: string;
    experiment_metadata: Record<string, any>;
    execution_summary: Record<string, any>;
    error_summary: Record<string, any>;
    aggregate_metrics: Record<string, any>[];
    runs: ExperimentRun[];
}
