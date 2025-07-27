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

const getRunId = (run: Run, index: number) => run.example_id_clean || `run-${index}`;

const getScoreClass = (score: number) => {
    if (score === 1.0) return "bg-green-500";
    if (score === 0.0) return "bg-red-500";
    return "bg-yellow-500";
};

const Filters = ({ runs, onFilterChange }: { runs: Run[], onFilterChange: (filteredRuns: Run[]) => void }) => {
    const [selectedFilters, setSelectedFilters] = useState<{ [key: string]: string }>({});

    const filterOptions = useMemo(() => {
        const options: { [key: string]: Set<number> } = {};
        runs.forEach(run => {
            run.annotations?.forEach(ann => {
                if (!options[ann.name]) options[ann.name] = new Set();
                options[ann.name].add(ann.score);
            });
        });
        Object.keys(options).forEach(key => {
            options[key] = new Set(Array.from(options[key]).sort((a, b) => a - b));
        });
        return options;
    }, [runs]);

    const handleFilterChange = (metricName: string, value: string) => {
        setSelectedFilters(prev => ({ ...prev, [metricName]: value }));
    };

    const applyFilters = () => {
        const activeFilters = Object.entries(selectedFilters).filter(([, value]) => value !== 'all' && value !== '');
        
        if (activeFilters.length === 0) {
            onFilterChange(runs);
            return;
        }

        const filtered = runs.filter(run => {
            return activeFilters.every(([metricName, value]) => {
                const annotation = run.annotations?.find(ann => ann.name === metricName);
                return annotation && annotation.score === parseFloat(value);
            });
        });
        onFilterChange(filtered);
    };

    const clearFilters = () => {
        setSelectedFilters({});
        onFilterChange(runs);
    };
    
    const desiredOrder = [
        "Answer Completeness", "Answer Similarity", "Activate Search Tools",
        "Golden Link in Answer", "Golden Link in Tool Calling",
    ];

    const sortedFilterNames = Object.keys(filterOptions).sort((a, b) => {
        const indexA = desiredOrder.indexOf(a);
        const indexB = desiredOrder.indexOf(b);
        if (indexA !== -1 && indexB !== -1) return indexA - indexB;
        if (indexA !== -1) return -1;
        if (indexB !== -1) return 1;
        return a.localeCompare(b);
    });

    return (
        <div className="p-4 border-b">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {sortedFilterNames.map(name => (
                    <div key={name} className="grid gap-2">
                        <Label htmlFor={`filter-${name}`}>{name}</Label>
                        <Select
                            value={selectedFilters[name] || 'all'}
                            onValueChange={(value) => handleFilterChange(name, value)}
                        >
                            <SelectTrigger id={`filter-${name}`}>
                                <SelectValue placeholder="Todos" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Todos</SelectItem>
                                {Array.from(filterOptions[name]).map(score => (
                                    <SelectItem key={score} value={String(score)}>{score.toFixed(1)}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                ))}
            </div>
            <div className="flex justify-end gap-2 mt-4">
                <Button onClick={applyFilters} size="sm">Aplicar</Button>
                <Button onClick={clearFilters} size="sm" variant="outline">Limpar</Button>
            </div>
        </div>
    );
};

const Metadata = ({ metadata }: { metadata: ExperimentMetadata | null }) => {
    if (!metadata) return null;

    return (
        <Card>
            <CardHeader>
                <CardTitle>Parâmetros do Experimento</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div>
                    <p className="font-semibold">Modelo de Avaliação:</p>
                    <p className="text-muted-foreground">{metadata.eval_model || "N/A"}</p>
                </div>
                <div>
                    <p className="font-semibold">Modelo de Resposta:</p>
                    <p className="text-muted-foreground">{metadata.final_repose_model || "N/A"}</p>
                </div>
                <div>
                    <p className="font-semibold">Temperatura:</p>
                    <p className="text-muted-foreground">{metadata.temperature ?? "N/A"}</p>
                </div>
                <div>
                    <p className="font-semibold">Ferramentas:</p>
                    <p className="text-muted-foreground">{metadata.tools?.join(", ") || "N/A"}</p>
                </div>
            </CardContent>
        </Card>
    );
};

const SummaryMetrics = ({ runs }: { runs: Run[] }) => {
    const summary = useMemo(() => {
        const metrics: { [key: string]: { scores: number[], counts: { [key: string]: number } } } = {};
        if (!runs) return { metrics: {}, totalRuns: 0 };

        runs.forEach((run) => {
            run.annotations?.forEach((ann) => {
                if (typeof ann.score === 'number' && !isNaN(ann.score)) {
                    if (!metrics[ann.name]) {
                        metrics[ann.name] = { scores: [], counts: {} };
                    }
                    metrics[ann.name].scores.push(ann.score);
                    const scoreStr = ann.score.toFixed(1);
                    metrics[ann.name].counts[scoreStr] = (metrics[ann.name].counts[scoreStr] || 0) + 1;
                }
            });
        });
        return { metrics, totalRuns: runs.length };
    }, [runs]);

    if (summary.totalRuns === 0) return null;

    const preferredOrder = [
        "Answer Completeness", "Answer Similarity", "Activate Search Tools",
        "Golden Link in Answer", "Golden Link in Tool Calling",
    ];

    const sortedMetricNames = Object.keys(summary.metrics).sort((a, b) => {
        const indexA = preferredOrder.indexOf(a);
        const indexB = preferredOrder.indexOf(b);
        if (indexA !== -1 && indexB !== -1) return indexA - indexB;
        if (indexA !== -1) return -1;
        if (indexB !== -1) return 1;
        return a.localeCompare(b);
    });

    return (
        <Card>
            <CardHeader>
                <CardTitle>Métricas Gerais ({summary.totalRuns} runs)</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sortedMetricNames.map(name => {
                    const metric = summary.metrics[name];
                    if (!metric || metric.scores.length === 0) return null;
                    const average = metric.scores.reduce((a, b) => a + b, 0) / metric.scores.length;
                    return (
                        <Card key={name} className="flex flex-col">
                            <CardHeader className="pb-2">
                                <CardDescription>{name}</CardDescription>
                                <CardTitle className="text-2xl">{average.toFixed(2)}</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {/* Distribution can be added here */}
                            </CardContent>
                        </Card>
                    );
                })}
            </CardContent>
        </Card>
    );
};

const Evaluations = ({ annotations }: { annotations: Annotation[] }) => {
    if (!annotations || annotations.length === 0) {
        return <p className="text-sm text-muted-foreground">Nenhuma avaliação disponível.</p>;
    }

    const preferredOrder = [
        "Answer Completeness", "Answer Similarity", "Activate Search Tools",
        "Golden Link in Answer", "Golden Link in Tool Calling",
    ];

    const sortedAnnotations = [...annotations].sort((a, b) => {
        const indexA = preferredOrder.indexOf(a.name);
        const indexB = preferredOrder.indexOf(b.name);
        if (indexA !== -1 && indexB !== -1) return indexA - indexB;
        if (indexA !== -1) return -1;
        if (indexB !== -1) return 1;
        return a.name.localeCompare(b.name);
    });

    return (
        <div className="space-y-2">
            {sortedAnnotations.map((ann, index) => (
                <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center gap-3">
                        <span className={`text-white text-xs font-bold px-2 py-1 rounded-full ${getScoreClass(ann.score)}`}>
                            {ann.score.toFixed(1)}
                        </span>
                        <p className="font-semibold">{ann.name}</p>
                    </div>
                    {ann.explanation && (
                        <div className="prose prose-sm dark:prose-invert max-w-none mt-2 pt-2 border-t">
                            {typeof ann.explanation === 'string' ? (
                                <div dangerouslySetInnerHTML={{ __html: marked(ann.explanation) }} />
                            ) : (
                                <pre className="p-4 bg-muted text-muted-foreground rounded-md text-xs">
                                    {JSON.stringify(ann.explanation, null, 2)}
                                </pre>
                            )}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
};

const ReasoningTimeline = ({ orderedSteps }: { orderedSteps: OrderedStep[] }) => {
    if (!orderedSteps || orderedSteps.length === 0) {
        return <p className="text-sm text-muted-foreground">Nenhum passo de raciocínio disponível.</p>;
    }

    let sequenceCounter = 0;
    let currentStepPrefix = "";

    const getIcon = (stepType: string) => {
        switch (stepType) {
            case "reasoning_message": return { icon: "bi-lightbulb" };
            case "tool_call_message": return { icon: "bi-tools" };
            case "tool_return_message": return { icon: "bi-box-arrow-in-left" };
            case "assistant_message": return { icon: "bi-chat-text" };
            case "letta_usage_statistics": return { icon: "bi-bar-chart-fill" };
            default: return { icon: '' };
        }
    };

    return (
        <Accordion type="multiple" className="w-full">
            {orderedSteps.map((step, index) => {
                let title: string = "";
                let content: React.ReactNode = null;
                const { icon: iconName } = getIcon(step.type);

                switch (step.type) {
                    case "reasoning_message":
                        sequenceCounter++;
                        currentStepPrefix = `${sequenceCounter}. `;
                        title = `${currentStepPrefix}Raciocínio`;
                        content = <p className="mb-0 italic" dangerouslySetInnerHTML={{ __html: `"${step.message.reasoning}"` }} />;
                        break;
                    case "tool_call_message":
                        title = `${currentStepPrefix}Chamada de Ferramenta: ${step.message.tool_call.name}`;
                        content = <pre className="p-4 bg-muted text-muted-foreground rounded-md text-xs">{JSON.stringify(step.message.tool_call.arguments, null, 2)}</pre>;
                        break;
                    case "tool_return_message":
                        title = `${currentStepPrefix}Retorno da Ferramenta: ${step.message.name}`;
                        content = <div className="prose prose-sm dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: marked(step.message.tool_return.text || '') }} />;
                        break;
                    case "assistant_message":
                        sequenceCounter++;
                        currentStepPrefix = `${sequenceCounter}. `;
                        title = `Mensagem do Assistente`;
                        content = <div className="prose prose-sm dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: marked(step.message.content) }} />;
                        break;
                    case "letta_usage_statistics":
                        title = "Estatísticas de Uso";
                        content = (
                            <div className="text-sm">
                                <p><strong>Tokens Totais:</strong> {step.message.total_tokens}</p>
                                <p><strong>Tokens de Prompt:</strong> {step.message.prompt_tokens}</p>
                                <p><strong>Tokens de Conclusão:</strong> {step.message.completion_tokens}</p>
                            </div>
                        );
                        break;
                    default:
                        return null;
                }

                return (
                    <AccordionItem value={`item-${index}`} key={index}>
                        <AccordionTrigger>
                            <div className="flex items-center gap-2">
                                <i className={`bi ${iconName}`}></i>
                                <span className="font-semibold text-left">{title}</span>
                            </div>
                        </AccordionTrigger>
                        <AccordionContent>
                            {content}
                        </AccordionContent>
                    </AccordionItem>
                );
            })}
        </Accordion>
    );
};

const Comparison = ({ run }: { run: Run }) => {
    const agentMessage = run.output.agent_output?.ordered?.find((m: OrderedStep) => m.type === "assistant_message");
    const agentAnswerHtml = agentMessage?.message?.content ? marked(agentMessage.message.content) : "<p>N/A</p>";
    const goldenAnswerHtml = run.reference_output.golden_answer ? marked(run.reference_output.golden_answer) : "<p>N/A</p>";

    return (
        <div className="grid md:grid-cols-2 gap-6">
            <Card>
                <CardHeader><CardTitle>🤖 Resposta do Agente</CardTitle></CardHeader>
                <CardContent className="prose prose-sm dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: agentAnswerHtml }} />
            </Card>
            <Card>
                <CardHeader><CardTitle>🏆 Resposta de Referência (Golden)</CardTitle></CardHeader>
                <CardContent className="prose prose-sm dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: goldenAnswerHtml }} />
            </Card>
        </div>
    );
};

const RunDetails = ({ run }: { run: Run }) => (
    <div className="space-y-6">
        <Card>
            <CardHeader><CardTitle>Mensagem do Usuário</CardTitle></CardHeader>
            <CardContent>
                {run.input.mensagem_whatsapp_simulada || "Mensagem não disponível"}
            </CardContent>
        </Card>
        <Comparison run={run} />
        <Card>
            <CardHeader><CardTitle>Avaliações</CardTitle></CardHeader>
            <CardContent>
                <Evaluations annotations={run.annotations} />
            </CardContent>
        </Card>
        <Card>
            <CardHeader><CardTitle>Cadeia de Pensamento (Reasoning)</CardTitle></CardHeader>
            <CardContent>
                <ReasoningTimeline orderedSteps={run.output.agent_output?.ordered} />
            </CardContent>
        </Card>
    </div>
);

const DetailsPlaceholder = () => (
    <div className="flex h-full items-center justify-center text-center text-muted-foreground">
        <div>
            <i className="bi bi-card-list text-6xl"></i>
            <p className="mt-4">Selecione um run na lista à esquerda para ver os detalhes.</p>
        </div>
    </div>
);

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
            { id: 'download-json', label: 'Baixar JSON', icon: 'bi-download', onClick: handleDownloadJson },
            { id: 'view-json', label: 'Ver JSON', icon: 'bi-file-earmark-code', onClick: () => setJsonModalOpen(true) }
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
            <div className="grid md:grid-cols-[350px_1fr] gap-4 p-4 h-[calc(100vh-135px)]">
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
