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
      ordered?: Array<Record<string, unknown>>;
    };
  };
  annotations: {
    name: string;
    score: number;
    explanation: string | Record<string, unknown>;
  }[];
}


export interface ExperimentData {
  experiment_metadata: Record<string, unknown>;
  experiment: Run[];
  dataset_name: string;
  experiment_name: string;

}
