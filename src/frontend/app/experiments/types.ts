// src/frontend/app/experiments/types.ts

// --- Base Schemas from Backend ---

export interface ReasoningStep {
    message_type: string;
    content: string | Record<string, any> | null;
}

export interface ConversationTurn {
    turn: number;
    user_message: string;
    agent_message: string | null;
    agent_reasoning_trace: ReasoningStep[] | null;
}

export interface EvaluationTask {
    id: string;
    prompt: string;
    [key: string]: any; // For other metadata columns
}

export interface EvaluationResult {
    score: number | null;
    annotations: string;
    has_error: boolean;
    error_message: string | null;
}

// Combined evaluation result with metadata from the runner
export interface Evaluation extends EvaluationResult {
    metric_name: string;
    duration_seconds: number;
}

export interface OneTurnAnalysis {
    agent_message: string | null;
    agent_reasoning_trace: ReasoningStep[] | null;
    evaluations: Evaluation[];
    has_error: boolean;
    error_message: string | null;
}

export interface MultiTurnAnalysis {
    final_agent_message: string | null;
    transcript: ConversationTurn[] | null;
    evaluations: Evaluation[];
    has_error: boolean;
    error_message: string | null;
}

// This is the main object for a single run, matching `TaskOutput` from the backend.
export interface ExperimentRun {
    duration_seconds: number;
    task_data: EvaluationTask;
    one_turn_analysis: OneTurnAnalysis;
    multi_turn_analysis: MultiTurnAnalysis;
}


// --- Aggregate and Info Schemas (Mostly Unchanged) ---

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

// This is the top-level object for the entire experiment data.
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