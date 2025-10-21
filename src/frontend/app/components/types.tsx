// app/lib/types.ts

export interface Dataset {
  id: string;
  name: string;
  description: string | null;
  exampleCount: number;
  experimentCount: number;
  createdAt: string;
}

export interface Experiment {
  id: string;
  name: string;
  description: string | null;
  createdAt: string;
  runCount: number;
  averageRunLatencyMs: number | null;
  errorRate: number;
  sequenceNumber: number;
  annotationSummaries: {
    annotationName: string;
    meanScore: number;
  }[];
}

export interface Example {
  id: string;
  latestRevision: {
    input: Record<string, unknown>;
    output: Record<string, unknown>;
    metadata: Record<string, unknown>;
  };
}

export interface Annotation {
  name: string;
  score: number;
  explanation: string | Record<string, unknown>;
}

export interface OrderedStep {
  type: 'reasoning_message' | 'tool_call_message' | 'tool_return_message' | 'assistant_message' | 'letta_usage_statistics';
  message: {
    reasoning?: string;
    tool_call?: {
      name: string;
      arguments: Record<string, unknown>;
    };
    name?: string;
    tool_return?: {
      text?: string;
      message?: string;
      web_search_queries?: string[];
      sources?: unknown[];
      documents?: Array<{
        title: string;
        collection: string;
        content: string;
        id: string;
        url: string;
      }>;
      metadata?: {
        total_tokens?: number;
      };
    };
    content?: string;
    total_tokens?: number;
    prompt_tokens?: number;
    completion_tokens?: number;
  };
}

export interface Run {
  example_id_clean: string;
  input: {
    mensagem_whatsapp_simulada: string;
  };
  reference_output: {
    golden_answer: string;
  };
  output: {
    agent_output?: {
      ordered?: OrderedStep[];
    };
    metadata?: {
      id?: string;
    };
  };
  annotations: Annotation[];
  tags?: string[];
}

export interface ExperimentMetadata {
  eval_model?: string;
  final_repose_model?: string;
  temperature?: number;
  tools?: string[];
  system_prompt?: string;
  system_prompt_answer_similatiry?: string;
}

export interface ExperimentData {
  experiment_metadata: ExperimentMetadata | null;
  experiment: Run[];
  dataset_name: string;
  experiment_name: string;
}
