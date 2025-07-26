'use client';

import React, { useState, useMemo, useEffect } from 'react';
import { marked } from 'marked';
import styles from '../page.module.css';
import { ExperimentData, Run, Annotation, OrderedStep, ExperimentMetadata } from '@/app/components/types';
import { useHeader } from '@/app/contexts/HeaderContext';
import JsonViewerModal from '@/app/components/JsonViewerModal'; // Import the modal
import { downloadFile } from '@/app/utils/csv'; // Import the download utility

// Props for the component
interface ExperimentDetailsClientProps {
  initialData: ExperimentData;
  datasetId: string;
  experimentId: string;
}

// Helper to get a unique ID for a run
const getRunId = (run: Run, index: number) => run.example_id_clean || `run-${index}`;

const getScoreClass = (score: number) => {
    if (score === 1.0) return styles.scoreHigh;
    if (score === 0.0) return styles.scoreLow;
    return styles.scoreMid;
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
        const activeFilters = Object.entries(selectedFilters).filter(([, value]) => value !== '');
        
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
        <div className={styles.filterContainer}>
            <div className={styles.filterGrid}>
                {sortedFilterNames.map(name => (
                    <div key={name} className={styles.filterItem}>
                        <label htmlFor={`filter-${name}`}>{name}</label>
                        <select
                            id={`filter-${name}`}
                            className="form-select form-select-sm"
                            value={selectedFilters[name] || ''}
                            onChange={(e) => handleFilterChange(name, e.target.value)}
                        >
                            <option value="">Todos</option>
                            {Array.from(filterOptions[name]).map(score => (
                                <option key={score} value={score}>{score.toFixed(1)}</option>
                            ))}
                        </select>
                    </div>
                ))}
            </div>
            <div className={styles.filterButtons}>
                <button onClick={applyFilters} className={`btn btn-sm ${styles.applyButton}`}>Aplicar</button>
                <button onClick={clearFilters} className={`btn btn-sm btn-outline-secondary ${styles.clearButton}`}>Limpar</button>
            </div>
        </div>
    );
};

const Metadata = ({ metadata }: { metadata: ExperimentMetadata }) => {
    if (!metadata) return null;

    const PromptSection = ({ title, content, collapseId }: { title: string, content: string | undefined, collapseId: string }) => {
        if (!content) return null;
        return (
            <div className={styles.metadataItemFullWidth}>
                <div className="d-flex align-items-center gap-2 mb-2">
                    <strong>{title}</strong>
                    <label className={`btn btn-sm btn-outline-secondary ${styles.collapseButton}`} htmlFor={collapseId}>
                        <i className="bi bi-arrows-expand me-1"></i> Ver/Ocultar
                    </label>
                </div>
                <input type="checkbox" className={styles.collapseInput} id={collapseId} />
                <div className={styles.collapseContent}>
                    <pre><code>{content}</code></pre>
                </div>
            </div>
        );
    };

    return (
        <div className={styles.card}>
            <h4 className="mb-3">Parâmetros do Experimento</h4>
            <div className={styles.metadataGrid}>
                <div className={styles.metadataItem}>
                    <strong>Modelo de Avaliação:</strong><br />
                    <span className="text-muted">{metadata.eval_model || "N/A"}</span>
                </div>
                <div className={styles.metadataItem}>
                    <strong>Modelo de Resposta:</strong><br />
                    <span className="text-muted">{metadata.final_repose_model || "N/A"}</span>
                </div>
                <div className={styles.metadataItem}>
                    <strong>Temperatura:</strong><br />
                    <span className="text-muted">{metadata.temperature ?? "N/A"}</span>
                </div>
                <div className={styles.metadataItem}>
                    <strong>Ferramentas:</strong><br />
                    <span className="text-muted">{metadata.tools?.join(", ") || "N/A"}</span>
                </div>
                <PromptSection title="System Prompt Principal" content={metadata.system_prompt} collapseId="systemPromptCollapse" />
                <PromptSection title="System Prompt (Similaridade)" content={metadata.system_prompt_answer_similatiry} collapseId="systemPromptSimilarityCollapse" />
            </div>
        </div>
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
        <div className={styles.card}>
            <h4 className="mb-3">Métricas Gerais ({summary.totalRuns} runs)</h4>
            <div className={styles.summaryGrid}>
                {sortedMetricNames.map(name => {
                    const metric = summary.metrics[name];
                    if (!metric || metric.scores.length === 0) return null;
                    const average = metric.scores.reduce((a, b) => a + b, 0) / metric.scores.length;
                    const sortedDistribution = Object.entries(metric.counts).sort(([scoreA], [scoreB]) => parseFloat(scoreB) - parseFloat(scoreA));

                    return (
                        <div className={styles.summaryMetricCard} key={name}>
                            <h6>{name}</h6>
                            <div className={styles.metricMainValue}>
                                {average.toFixed(2)} <small className="text-muted h6 fw-normal">avg</small>
                            </div>
                            <div className={styles.metricDistributionHeader}>Dist.</div>
                            {sortedDistribution.map(([score, count]) => {
                                const percentage = (count / metric.scores.length) * 100;
                                return (
                                    <div className={styles.distributionItem} key={score}>
                                        <span className="fw-bold">{score}</span>
                                        <div className={styles.distributionBarBg}>
                                            <div className={styles.distributionBar} style={{ width: `${percentage.toFixed(2)}%` }}></div>
                                        </div>
                                        <span className="text-muted small">{count} ({percentage.toFixed(0)}%)</span>
                                    </div>
                                );
                            })}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};


const Evaluations = ({ annotations, runId }: { annotations: Annotation[], runId: string }) => {
    if (!annotations || annotations.length === 0) {
        return <p>Nenhuma avaliação disponível.</p>;
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

    return sortedAnnotations.map((ann, index) => {
        const explanationContentHtml = ann.explanation
            ? typeof ann.explanation === 'object'
                ? `<pre><code>${JSON.stringify(ann.explanation, null, 2)}</code></pre>`
                : marked(ann.explanation)
            : '';
        const isJsonExplanation = typeof ann.explanation === 'object';
        const collapseId = `collapse-explanation-${runId}-${index}`;

        return (
            <div className={styles.evaluationCard} key={index}>
                <div className={styles.evaluationHeader}>
                    <div className={`${styles.score} ${getScoreClass(ann.score)}`}>{ann.score.toFixed(1)}</div>
                    <p className="fw-bold mb-0">{ann.name}</p>
                </div>
                {explanationContentHtml && (
                    <div className={styles.explanation}>
                        {isJsonExplanation ? (
                            <>
                                <input type="checkbox" className={styles.collapseInput} id={collapseId} />
                                <label className={`btn btn-sm btn-outline-secondary mb-2 ${styles.collapseButton}`} htmlFor={collapseId}>
                                    <i className="bi bi-arrows-expand me-1"></i> Ver Detalhes
                                </label>
                                <div className={styles.collapseContent}>
                                    <div dangerouslySetInnerHTML={{ __html: explanationContentHtml }} />
                                </div>
                            </>
                        ) : (
                            <div dangerouslySetInnerHTML={{ __html: explanationContentHtml }} />
                        )}
                    </div>
                )}
            </div>
        );
    });
};

const ReasoningTimeline = ({ orderedSteps }: { orderedSteps: OrderedStep[] }) => {
    if (!orderedSteps || orderedSteps.length === 0) {
        return <p className="text-muted">Nenhum passo de raciocínio disponível.</p>;
    }

    let sequenceCounter = 0;
    let currentStepPrefix = "";

    const getIcon = (stepType: string) => {
        switch (stepType) {
            case "reasoning_message": return { class: styles.timelineIconReasoning, icon: "bi-lightbulb" };
            case "tool_call_message": return { class: styles.timelineIconToolcall, icon: "bi-tools" };
            case "tool_return_message": return { class: styles.timelineIconReturn, icon: "bi-box-arrow-in-left" };
            case "assistant_message": return { class: styles.timelineIconAssistant, icon: "bi-chat-text" };
            case "letta_usage_statistics": return { class: styles.timelineIconStats, icon: "bi-bar-chart-fill" };
            default: return { class: '', icon: '' };
        }
    };

    return (
        <div className={styles.timeline}>
            {orderedSteps.map((step, index) => {
                let title: string = "";
                let content: React.ReactNode = null;
                const { class: iconClass, icon: iconName } = getIcon(step.type);

                switch (step.type) {
                    case "reasoning_message":
                        sequenceCounter++;
                        currentStepPrefix = `${sequenceCounter}. `;
                        title = `${currentStepPrefix}Raciocínio`;
                        content = <p className="mb-0 fst-italic" dangerouslySetInnerHTML={{ __html: `"${step.message.reasoning}"` }} />;
                        break;
                    case "tool_call_message":
                        title = `${currentStepPrefix}Chamada de Ferramenta: ${step.message.tool_call.name}`;
                        content = <pre>{JSON.stringify(step.message.tool_call.arguments, null, 2)}</pre>;
                        break;
                    case "tool_return_message":
                        title = `${currentStepPrefix}Retorno da Ferramenta: ${step.message.name}`;
                        const toolReturn = step.message.tool_return;
                        const collapseId = `collapse-sources-${index}`;
                        
                        const sections = [];
                        if (toolReturn.text) {
                            sections.push(
                                <div key="text" className={styles.toolReturnSection}>
                                    <hr className={styles.dashedSeparator} />
                                    <strong>Content:</strong>
                                    <div dangerouslySetInnerHTML={{ __html: marked(toolReturn.text) }} />
                                </div>
                            );
                        }
                        if (toolReturn.sources && toolReturn.sources.length > 0) {
                            sections.push(
                                <div key="sources" className={styles.toolReturnSection}>
                                    <div className={styles.toolReturnHeader}>
                                        <strong>Sources:</strong>
                                        <label className={`btn btn-sm btn-outline-secondary ${styles.collapseButton}`} htmlFor={collapseId}>
                                            <i className="bi bi-arrows-expand me-1"></i> Ver/Ocultar
                                        </label>
                                    </div>
                                    <input type="checkbox" className={styles.collapseInput} id={collapseId} />
                                    <div className={styles.collapseContent}>
                                        <pre>{JSON.stringify(toolReturn.sources, null, 2)}</pre>
                                    </div>
                                </div>
                            );
                        }
                        if (toolReturn.web_search_queries && toolReturn.web_search_queries.length > 0) {
                            sections.push(
                                <div key="queries" className={styles.toolReturnSection}>
                                    <strong>Web Search Queries:</strong>
                                    <pre>{JSON.stringify(toolReturn.web_search_queries, null, 2)}</pre>
                                </div>
                            );
                        }

                        content = (
                            <div>
                                {sections.map((section, i) => (
                                    <React.Fragment key={i}>
                                        {i > 0 && <hr className={styles.dashedSeparator} />}
                                        {section}
                                    </React.Fragment>
                                ))}
                            </div>
                        );
                        break;
                    case "assistant_message":
                        sequenceCounter++;
                        currentStepPrefix = `${sequenceCounter}. `;
                        title = `Mensagem do Assistente`;
                        content = <div dangerouslySetInnerHTML={{ __html: marked(step.message.content) }} />;
                        break;
                    case "letta_usage_statistics":
                        title = "Estatísticas de Uso";
                        content = (
                            <div>
                                <p className="mb-0"><strong>Tokens Totais:</strong> {step.message.total_tokens}</p>
                                <p className="mb-0"><strong>Tokens de Prompt:</strong> {step.message.prompt_tokens}</p>
                                <p className="mb-0"><strong>Tokens de Conclusão:</strong> {step.message.completion_tokens}</p>
                            </div>
                        );
                        break;
                    default:
                        return null;
                }

                return (
                    <div className={styles.timelineItem} key={index}>
                        <div className={`${styles.timelineIcon} ${iconClass}`}>
                            <i className={`bi ${iconName}`}></i>
                        </div>
                        <div className={styles.timelineContent}>
                            <h4>{title}</h4>
                            {content}
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

const Comparison = ({ run }: { run: Run }) => {
    const agentMessage = run.output.agent_output?.ordered?.find((m: any) => m.type === "assistant_message");
    const agentAnswerHtml = agentMessage?.message?.content ? marked(agentMessage.message.content) : "<p>N/A</p>";
    const goldenAnswerHtml = run.reference_output.golden_answer ? marked(run.reference_output.golden_answer) : "<p>N/A</p>";

    return (
        <div className={styles.comparisonGrid}>
            <div className={styles.comparisonBox}>
                <h5>🤖 Resposta do Agente</h5>
                <div className="agent-answer-content" dangerouslySetInnerHTML={{ __html: agentAnswerHtml }} />
            </div>
            <div className={styles.comparisonBox}>
                <h5>🏆 Resposta de Referência (Golden)</h5>
                <div className="golden-answer-content" dangerouslySetInnerHTML={{ __html: goldenAnswerHtml }} />
            </div>
        </div>
    );
};

const RunDetails = ({ run }: { run: Run }) => (
    <>
        <div className={styles.card}>
            <h4 className="section-title">Mensagem do Usuário</h4>
            <div className={styles.comparisonBox}>
                {run.input.mensagem_whatsapp_simulada || "Mensagem não disponível"}
            </div>

            <h4 className="section-title mb-3 mt-4">Comparação de Respostas</h4>
            <Comparison run={run} />
        </div>

        <div className={styles.card}>
            <h4 className="section-title">Avaliações</h4>
            <Evaluations annotations={run.annotations} runId={getRunId(run, -1)} />
        </div>

        <div className={styles.card}>
            <div className="section-header">
                <h4 className="section-title">Cadeia de Pensamento (Reasoning)</h4>
            </div>
            <ReasoningTimeline orderedSteps={run.output.agent_output?.ordered} />
        </div>
    </>
);

const DetailsPlaceholder = () => (
    <div className="d-flex h-100 align-items-center justify-content-center text-center text-muted p-4">
        <div>
            <i className="bi bi-card-list" style={{ fontSize: '3rem' }}></i>
            <p className="mt-2">Selecione um run na lista à esquerda para ver os detalhes.</p>
        </div>
    </div>
);

export default function ExperimentDetailsClient({ initialData }: ExperimentDetailsClientProps) {
    const { experiment: runs, experiment_metadata, dataset_name, experiment_name } = initialData;
    const { setTitle, setSubtitle, setPageActions } = useHeader();
    const [isJsonModalOpen, setJsonModalOpen] = useState(false);

    const [filteredRuns, setFilteredRuns] = useState(runs);
    const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

    const handleDownloadJson = () => {
        const jsonString = JSON.stringify(initialData, null, 2);
        downloadFile(
            `experiment_${initialData.experiment_name}.json`,
            jsonString,
            'application/json'
        );
    };

    useEffect(() => {
        setTitle('Detalhes do Experimento');
        const newSubtitle = `${dataset_name || 'Dataset'} <br /> ${experiment_name || 'Experimento'}`;
        setSubtitle(newSubtitle);

        // Add page-specific actions
        setPageActions([
            {
                id: 'download-json',
                label: 'Baixar JSON',
                icon: 'bi-download',
                onClick: handleDownloadJson,
            },
            {
                id: 'view-json',
                label: 'Ver JSON',
                icon: 'bi-file-earmark-code',
                onClick: () => setJsonModalOpen(true),
            }
        ]);

        // Clear actions on component unmount
        return () => {
            setPageActions([]);
        };
    }, [dataset_name, experiment_name, setTitle, setSubtitle, setPageActions]);
    
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
                <JsonViewerModal 
                    data={initialData} 
                    onClose={() => setJsonModalOpen(false)} 
                />
            )}
            <div className={styles.twoColumnLayout}>
                <aside className={styles.runListColumn}>
                    <Filters runs={runs} onFilterChange={handleFilterChange} />
                    <div className={styles.runListHeader}>
                        <h5 className="mb-0">Execuções (Runs)</h5>
                        <span className={`badge bg-secondary-subtle text-secondary-emphasis rounded-pill ${styles.runCountBadge}`}>{filteredRuns.length}</span>
                    </div>
                    <div className={`${styles.runList} list-group list-group-flush`}>
                        {filteredRuns.map((run, index) => {
                            const runId = getRunId(run, index);
                            return (
                                <div
                                    key={runId}
                                    className={`${styles.runListItem} ${selectedRunId === runId ? styles.active : ''}`}
                                    onClick={() => setSelectedRunId(runId)}
                                >
                                    <span className={styles.runListItemId}>ID: {run.output?.metadata?.id || runId}</span>
                                </div>
                            );
                        })}
                    </div>
                </aside>

                <main className={styles.detailsColumn}>
                    <Metadata metadata={experiment_metadata} />
                    <SummaryMetrics runs={runs} />
                    {selectedRun ? <RunDetails run={selectedRun} /> : <DetailsPlaceholder />}
                </main>
            </div>
        </>
    );
}
