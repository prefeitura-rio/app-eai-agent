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
    className=""
  >
    <div className="">ID: {run.example_id_clean}</div>
  </a>
);

const DetailsPlaceholder = () => (
    <div className="">
        <div>
            <p className="">Selecione um run na lista à esquerda para ver os detalhes.</p>
        </div>
    </div>
);

const RunDetails = ({ run }: { run: Run }) => {
    const agentMessage = run.output?.agent_output?.ordered?.find(m => m.type === 'assistant_message');
    const agentAnswer = (agentMessage?.message as { content: string })?.content || 'N/A';
    const goldenAnswer = run.reference_output.golden_answer || 'N/A';

    return (
        <div className="">
            <div>
                <h4 className="">Mensagem do Usuário</h4>
                <div className="">
                    {run.input.mensagem_whatsapp_simulada}
                </div>
            </div>

            <div>
                <h4 className="">Comparação de Respostas</h4>
                <div className="">
                    <div className="">
                        <h5 className="">Resposta do Agente</h5>
                        <div className="" dangerouslySetInnerHTML={{ __html: agentAnswer }}></div>
                    </div>
                    <div className="">
                        <h5 className="">Resposta de Referência</h5>
                        <div className="" dangerouslySetInnerHTML={{ __html: goldenAnswer }}></div>
                    </div>
                </div>
            </div>
            
            <div>
                <h4 className="">Avaliações</h4>
                <div className="">
                    {run.annotations.map(ann => (
                        <div key={ann.name} className="">
                            <div className="">
                                <span className="">{ann.name}</span>
                                <span className="">{ann.score.toFixed(2)}</span>
                            </div>
                            {ann.explanation && <pre className="">{JSON.stringify(ann.explanation, null, 2)}</pre>}
                        </div>
                    ))}
                </div>
            </div>

            <div>
                <h4 className="">Cadeia de Pensamento (Reasoning)</h4>
                <div className="">A timeline de eventos será implementada aqui.</div>
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
    <div className="">
      <div className="">
        <div className="">
          <h5 className="">Execuções ({data.experiment.length})</h5>
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

      <div className="">
        {selectedRun ? <RunDetails run={selectedRun} /> : <DetailsPlaceholder />}
      </div>
    </div>
  );
}