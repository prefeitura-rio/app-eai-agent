'use client';

import React, { useState, useMemo } from 'react';
import { ExperimentData, Run } from '@/app/components/types';

interface ExperimentDetailsClientProps {
  initialData: ExperimentData;
  datasetId: string;
  experimentId: string;
}

const RunListItem = ({ run, isSelected, onClick }: { run: Run, isSelected: boolean, onClick: () => void }) => (
  <a
    href="#"
    onClick={(e) => {
      e.preventDefault();
      onClick();
    }}
    className={`block p-3 border-b border-gray-200 dark:border-gray-700 ${
      isSelected ? 'bg-indigo-100 dark:bg-indigo-900' : 'hover:bg-gray-100 dark:hover:bg-gray-700'
    }`}
  >
    <div className="font-semibold text-sm text-gray-800 dark:text-gray-200">ID: {run.example_id_clean}</div>
  </a>
);

const DetailsPlaceholder = () => (
    <div className="flex h-full items-center justify-center text-center text-gray-500 dark:text-gray-400">
        <div>
            <p className="mt-2">Selecione um run na lista à esquerda para ver os detalhes.</p>
        </div>
    </div>
);

const RunDetails = ({ run }: { run: Run }) => {
    const agentMessage = run.output?.agent_output?.ordered?.find(m => m.type === 'assistant_message');
    const agentAnswer = (agentMessage?.message as { content: string })?.content || 'N/A';
    const goldenAnswer = run.reference_output.golden_answer || 'N/A';

    return (
        <div className="p-4 space-y-6">
            <div>
                <h4 className="text-lg font-semibold mb-2">Mensagem do Usuário</h4>
                <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded-md text-sm">
                    {run.input.mensagem_whatsapp_simulada}
                </div>
            </div>

            <div>
                <h4 className="text-lg font-semibold mb-2">Comparação de Respostas</h4>
                <div className="grid md:grid-cols-2 gap-4">
                    <div className="p-3 border border-gray-200 dark:border-gray-700 rounded-md">
                        <h5 className="text-md font-semibold mb-2">Resposta do Agente</h5>
                        <div className="prose prose-sm dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: agentAnswer }}></div>
                    </div>
                    <div className="p-3 border border-gray-200 dark:border-gray-700 rounded-md">
                        <h5 className="text-md font-semibold mb-2">Resposta de Referência</h5>
                        <div className="prose prose-sm dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: goldenAnswer }}></div>
                    </div>
                </div>
            </div>
            
            <div>
                <h4 className="text-lg font-semibold mb-2">Avaliações</h4>
                <div className="space-y-4">
                    {run.annotations.map(ann => (
                        <div key={ann.name} className="p-3 border border-gray-200 dark:border-gray-700 rounded-md">
                            <div className="flex justify-between items-center">
                                <span className="font-semibold">{ann.name}</span>
                                <span className={`px-2 py-1 text-xs font-bold rounded-full ${ann.score > 0.5 ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>{ann.score.toFixed(2)}</span>
                            </div>
                            {ann.explanation && <pre className="mt-2 text-xs bg-gray-100 dark:bg-gray-700 p-2 rounded-md overflow-auto">{JSON.stringify(ann.explanation, null, 2)}</pre>}
                        </div>
                    ))}
                </div>
            </div>

            <div>
                <h4 className="text-lg font-semibold mb-2">Cadeia de Pensamento (Reasoning)</h4>
                <div className="text-sm text-gray-500">A timeline de eventos será implementada aqui.</div>
            </div>
        </div>
    );
};


export default function ExperimentDetailsClient({ initialData }: ExperimentDetailsClientProps) {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [data, setData] = useState<ExperimentData>(initialData);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  const selectedRun = useMemo(() => {
    if (!selectedRunId) return null;
    return data.experiment.find(run => run.example_id_clean === selectedRunId);
  }, [data, selectedRunId]);

  return (
    <div className="flex h-full">
      <div className="w-1/4 h-full flex-shrink-0 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h5 className="font-semibold">Execuções ({data.experiment.length})</h5>
        </div>
        <div>
          {data.experiment.map(run => (
            <RunListItem
              key={run.example_id_clean}
              run={run}
              isSelected={run.example_id_clean === selectedRunId}
              onClick={() => setSelectedRunId(run.example_id_clean)}
            />
          ))}
        </div>
      </div>

      <div className="flex-grow h-full overflow-y-auto">
        {selectedRun ? <RunDetails run={selectedRun} /> : <DetailsPlaceholder />}
      </div>
    </div>
  );
}