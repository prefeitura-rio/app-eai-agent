// src/frontend/app/experiments/types.ts

export interface DatasetInfo {
    dataset_id: string;
    dataset_name: string;
    dataset_description: string;
    num_examples: number;
    num_runs: number;
    created_at: string;
}

export interface ScoreStatistics {
    average: number;
    median: number;
    min: number;
    max: number;
    std_dev: number;
}

export interface DurationStatistics {
    average: number;
    median: number;
    min: number;
    max: number;
    std_dev: number;
}

export interface ScoreDistribution {
    value: number;
    count: number;
    percentage: number;
}

export interface AggregateMetric {
    metric_name: string;
    score_statistics: ScoreStatistics | null;
    duration_statistics_seconds: DurationStatistics;
    score_distribution: ScoreDistribution[];
    total_runs: number;
    successful_runs: number;
    failed_runs: number;
}

export interface DatasetExperimentInfo {
    dataset_id: string;
    experiment_id: string;
    experiment_name: string;
    experiment_description: string;
    experiment_timestamp: string; // Datetime string
    execution_summary: {
        total_duration_seconds: number;
        [key: string]: unknown;
    };
    error_summary: Record<string, unknown>;
    aggregate_metrics: AggregateMetric[];
}

export interface DatasetExample {
    id: string;
    prompt: string;
    [key: string]: unknown; // Allow other metadata fields
}

export interface DatasetExamplesInfo {
    dataset_id: string;
    num_examples: number;
    examples: DatasetExample[];
}

interface Turn {
    turn: number;
    judge_message: string;
    agent_response: string;
    [key: string]: unknown;
}

export interface ExperimentRun {
    duration_seconds: number;
    task_data: {
        id: string;
        prompt?: string;
        [key: string]: unknown;
    };
    agent_response: {
        one_turn: string | null;
        multi_turn_final: string | null;
    };
    reasoning_trace: {
        one_turn: { message_type: string; [key: string]: unknown }[] | null;
        multi_turn: Turn[] | null;
    };
    evaluations: {
        metric_name: string;
        score: number | null;
        judge_annotations: string | null;
        eval_type?: 'one' | 'multiple';
        [key: string]: unknown;
    }[];
    [key: string]: unknown;
}

export interface ExperimentDetails {
    dataset_id: string;
    dataset_name: string;
    dataset_description: string;
    experiment_id: string;
    experiment_name: string;
    experiment_description: string;
    experiment_timestamp: string;
    experiment_metadata: {
        agent_config?: {
            model?: string;
            tools?: string[];
            system?: string;
            [key: string]: unknown;
        };
        judge_model?: string;
        judges_prompts?: Record<string, string>;
        [key: string]: unknown;
    };
    execution_summary: {
        total_duration_seconds: number;
        average_task_duration_seconds: number;
        average_metric_duration_seconds: number;
        [key: string]: unknown;
    };
    error_summary: Record<string, unknown>;
    aggregate_metrics: AggregateMetric[];
    runs: ExperimentRun[];
}
