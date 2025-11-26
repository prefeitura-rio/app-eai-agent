import React from 'react';
import { Search, Lightbulb } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import JsonViewer from './JsonViewer';
import { InstrucaoItem } from '../../types/chat';

// Configurar marked para processar quebras de linha
marked.use({ breaks: true });

interface ToolReturnViewerProps {
  toolReturn: unknown;
  toolName?: string;
}

const ToolReturnViewer = ({ toolReturn, toolName }: ToolReturnViewerProps) => {
  try {
    const data = typeof toolReturn === 'string' ? JSON.parse(toolReturn) : toolReturn;
    
    if (typeof data !== 'object' || data === null) {
      return <p className="p-2 bg-muted/50 rounded-md text-base-custom whitespace-pre-wrap break-all font-mono">{String(data)}</p>;
    }

    // Special handling for specific tools
    if (toolName === 'google_search') {
      // Detectar se é resposta do Typesense ou Google
      const hasTypesenseResponse = 'response' in data && Array.isArray(data.response);

      if (hasTypesenseResponse) {
        // Formato Typesense
        const typesenseResults = data.response as Array<{
          title: string;
          description: string;
          category: string;
          hint: string;
          custo_servico: string;
          descricao_completa: string;
          is_free: string;
          orgao_gestor: string[];
          publico_especifico: string[];
          documentos_necessarios: string[];
          instrucoes_solicitante: string;
          legislacao_relacionada: string[];
          resultado_solicitacao: string;
          resumo_plaintext: string;
          servico_nao_cobre: string;
          tempo_atendimento: string;
          score_info: Record<string, unknown>;
          ai_score: Record<string, unknown>;
        }>;

        return (
          <div className="space-y-4">
            <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-950 rounded-md border border-blue-200 dark:border-blue-800">
              <Search className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                Resultados do Hub ({typesenseResults.length})
              </span>
            </div>

            {typesenseResults.map((result, index) => (
              <div key={index} className="border border-border rounded-lg p-4 space-y-3 bg-card">
                {/* Título e Categoria */}
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-semibold text-lg text-foreground">{result.title}</h4>
                    {result.category && (
                      <Badge variant="secondary" className="shrink-0">{result.category}</Badge>
                    )}
                  </div>
                  {result.description && (
                    <p className="text-sm text-muted-foreground">{result.description}</p>
                  )}
                </div>

                {/* Hint da Ferramenta */}
                {result.hint && (
                  <div className="bg-yellow-50 dark:bg-yellow-950/30 border border-yellow-200 dark:border-yellow-800 rounded-md p-3">
                    <div className="flex items-start gap-2">
                      <Lightbulb className="h-4 w-4 text-yellow-600 dark:text-yellow-500 mt-0.5 shrink-0" />
                      <div className="text-sm text-yellow-800 dark:text-yellow-200">
                        <strong>Dica:</strong> {result.hint}
                      </div>
                    </div>
                  </div>
                )}

                {/* Accordion com Detalhes */}
                <Accordion type="single" collapsible className="w-full">
                  <AccordionItem value={`details-${index}`} className="border-none">
                    <AccordionTrigger className="text-sm font-medium hover:no-underline">
                      Ver Detalhes Completos
                    </AccordionTrigger>
                    <AccordionContent className="space-y-3 pt-3">

                      {/* Descrição Completa */}
                      {result.descricao_completa && (
                        <div>
                          <h5 className="font-medium text-sm text-muted-foreground mb-1">Descrição Completa</h5>
                          <div
                            className="prose prose-sm dark:prose-invert max-w-none"
                            dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(result.descricao_completa, { breaks: true }) as string) }}
                          />
                        </div>
                      )}

                      {/* Informações Gerais */}
                      <div className="grid grid-cols-2 gap-3">
                        {result.custo_servico && (
                          <div>
                            <h5 className="font-medium text-sm text-muted-foreground mb-1">Custo</h5>
                            <p className="text-sm">{result.custo_servico}</p>
                          </div>
                        )}
                        {result.tempo_atendimento && (
                          <div>
                            <h5 className="font-medium text-sm text-muted-foreground mb-1">Tempo de Atendimento</h5>
                            <p className="text-sm">{result.tempo_atendimento}</p>
                          </div>
                        )}
                        {result.is_free && (
                          <div>
                            <h5 className="font-medium text-sm text-muted-foreground mb-1">Gratuito</h5>
                            <p className="text-sm">{result.is_free}</p>
                          </div>
                        )}
                      </div>

                      {/* Órgão Gestor */}
                      {result.orgao_gestor && result.orgao_gestor.length > 0 && (
                        <div>
                          <h5 className="font-medium text-sm text-muted-foreground mb-1">Órgão Gestor</h5>
                          <div className="flex flex-wrap gap-1">
                            {result.orgao_gestor.map((orgao, idx) => (
                              <Badge key={idx} variant="outline">{orgao}</Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Público Específico */}
                      {result.publico_especifico && result.publico_especifico.length > 0 && (
                        <div>
                          <h5 className="font-medium text-sm text-muted-foreground mb-1">Público Específico</h5>
                          <div className="flex flex-wrap gap-1">
                            {result.publico_especifico.map((publico, idx) => (
                              <Badge key={idx} variant="secondary">{publico}</Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Documentos Necessários */}
                      {result.documentos_necessarios && result.documentos_necessarios.length > 0 && (
                        <div>
                          <h5 className="font-medium text-sm text-muted-foreground mb-2">Documentos Necessários</h5>
                          <ul className="list-disc list-inside space-y-1 text-sm">
                            {result.documentos_necessarios.map((doc, idx) => (
                              <li key={idx}>{doc}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Instruções ao Solicitante */}
                      {result.instrucoes_solicitante && (
                        <div>
                          <h5 className="font-medium text-sm text-muted-foreground mb-1">Instruções ao Solicitante</h5>
                          <div
                            className="prose prose-sm dark:prose-invert max-w-none"
                            dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(result.instrucoes_solicitante, { breaks: true }) as string) }}
                          />
                        </div>
                      )}

                      {/* Resultado da Solicitação */}
                      {result.resultado_solicitacao && (
                        <div>
                          <h5 className="font-medium text-sm text-muted-foreground mb-1">Resultado da Solicitação</h5>
                          <div
                            className="prose prose-sm dark:prose-invert max-w-none"
                            dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(result.resultado_solicitacao, { breaks: true }) as string) }}
                          />
                        </div>
                      )}

                      {/* O que o serviço não cobre */}
                      {result.servico_nao_cobre && (
                        <div>
                          <h5 className="font-medium text-sm text-muted-foreground mb-1">O que o serviço NÃO cobre</h5>
                          <div
                            className="prose prose-sm dark:prose-invert max-w-none"
                            dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(result.servico_nao_cobre, { breaks: true }) as string) }}
                          />
                        </div>
                      )}

                      {/* Legislação Relacionada */}
                      {result.legislacao_relacionada && result.legislacao_relacionada.length > 0 && (
                        <div>
                          <h5 className="font-medium text-sm text-muted-foreground mb-2">Legislação Relacionada</h5>
                          <ul className="list-disc list-inside space-y-1 text-sm">
                            {result.legislacao_relacionada.map((lei, idx) => (
                              <li key={idx}>{lei}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Scores (Debug Info) */}
                      {(result.score_info || result.ai_score) && (
                        <Accordion type="single" collapsible>
                          <AccordionItem value="scores" className="border-t">
                            <AccordionTrigger className="text-xs text-muted-foreground">
                              Informações de Score (Debug)
                            </AccordionTrigger>
                            <AccordionContent>
                              <div className="space-y-2">
                                {result.score_info && Object.keys(result.score_info).length > 0 && (
                                  <div>
                                    <p className="text-xs font-medium mb-1">Score Info:</p>
                                    <JsonViewer data={result.score_info} />
                                  </div>
                                )}
                                {result.ai_score && Object.keys(result.ai_score).length > 0 && (
                                  <div>
                                    <p className="text-xs font-medium mb-1">AI Score:</p>
                                    <JsonViewer data={result.ai_score} />
                                  </div>
                                )}
                              </div>
                            </AccordionContent>
                          </AccordionItem>
                        </Accordion>
                      )}

                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              </div>
            ))}
          </div>
        );
      } else {
        // Formato Google Original
        const entries = Object.entries(data);
        const orderedFields = ['text', 'web_search_queries', 'sources', 'id'];
        const orderedEntries = [];

        // Add fields in the specified order
        for (const field of orderedFields) {
          const entry = entries.find(([key]) => key === field);
          if (entry) {
            orderedEntries.push(entry);
          }
        }

        // Add any remaining fields
        for (const entry of entries) {
          if (!orderedFields.includes(entry[0])) {
            orderedEntries.push(entry);
          }
        }

        return (
          <div className="space-y-2">
            <div className="flex items-center gap-2 px-3 py-2 bg-green-50 dark:bg-green-950 rounded-md border border-green-200 dark:border-green-800">
              <Search className="h-4 w-4 text-green-600 dark:text-green-400" />
              <span className="text-sm font-medium text-green-600 dark:text-green-400">
                Resultados do Google Search
              </span>
            </div>
            {orderedEntries.map(([key, value]) => (
              <div key={key} className="space-y-1">
                <h5 className="font-medium text-base-custom capitalize text-muted-foreground">{key.replace(/_/g, ' ')}</h5>
                <div className="pl-4">
                  {key === 'sources' ? (
                    <Accordion type="single" collapsible className="w-full">
                      <AccordionItem value="sources" className="border-none">
                        <AccordionTrigger className="text-base-custom p-2 hover:no-underline">
                          Ver Fontes
                        </AccordionTrigger>
                        <AccordionContent>
                          {typeof value === 'string' ? (
                            <div
                              className="prose prose-base dark:prose-invert max-w-none whitespace-pre-wrap prose-base-custom"
                              dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(value, { breaks: true }) as string) }}
                            />
                          ) : (
                            <pre className="text-base-custom font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
                              {JSON.stringify(value, null, 2)}
                            </pre>
                          )}
                        </AccordionContent>
                      </AccordionItem>
                    </Accordion>
                  ) : typeof value === 'string' ? (
                    <div
                      className="prose prose-base dark:prose-invert max-w-none whitespace-pre-wrap prose-base-custom"
                      dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(value, { breaks: true }) as string) }}
                    />
                  ) : (
                    <pre className="text-base-custom font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
                      {JSON.stringify(value, null, 2)}
                    </pre>
                  )}
                </div>
              </div>
            ))}
          </div>
        );
      }
    } else if (toolName === 'equipments_instructions') {
      // Special handling for equipments_instructions
      const toolReturnData = data as {
        tema?: string;
        next_tool_instructions?: string;
        next_too_instructions?: string;
        instrucoes?: Array<{
          tema?: string;
          instrucoes?: string;
        }>;
        categorias?: unknown;
      };
      
      return (
        <div className="space-y-4">
          {(toolReturnData.next_tool_instructions || toolReturnData.next_too_instructions) && (
            <div className="space-y-1">
              <h5 className="font-medium text-base-custom capitalize text-muted-foreground">Próximas Instruções</h5>
              <div className="pl-4">
                <div
                  className="prose prose-base dark:prose-invert max-w-none whitespace-pre-wrap prose-base-custom"
                  dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(toolReturnData.next_tool_instructions || toolReturnData.next_too_instructions || '', { breaks: true }) as string) }}
                />
              </div>
            </div>
          )}
          
          {toolReturnData.tema && (
            <div className="space-y-1">
              <h5 className="font-medium text-base-custom capitalize text-muted-foreground">Tema</h5>
              <div className="pl-4">
                <div className="text-base-custom font-medium text-foreground">
                  {toolReturnData.tema}
                </div>
              </div>
            </div>
          )}
          
          {toolReturnData.instrucoes && Array.isArray(toolReturnData.instrucoes) && (
            <div className="space-y-1">
              <h5 className="font-medium text-base-custom capitalize text-muted-foreground">Instruções</h5>
              <div className="pl-4 space-y-3">
                {toolReturnData.instrucoes.map((item: InstrucaoItem, index: number) => (
                  <div key={index} className="border-l-2 border-primary/20 pl-3">
                    {/* Renderiza tema primeiro se existir */}
                    {item.tema && (
                      <div className="text-base-custom text-muted-foreground mb-2">
                        <span className="font-medium">Tema:</span> {item.tema}
                      </div>
                    )}
                    {/* Renderiza instruções se existir */}
                    {item.instrucoes && typeof item.instrucoes === 'string' && (
                      <div
                        className="prose prose-base dark:prose-invert max-w-none whitespace-pre-wrap prose-base-custom"
                        dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(item.instrucoes, { breaks: true }) as string) }}
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {Boolean(toolReturnData.categorias) && (
            <div className="space-y-1">
              <h5 className="font-medium text-base-custom capitalize text-muted-foreground">Categorias</h5>
              <div className="pl-4">
                <JsonViewer data={toolReturnData.categorias as object} />
              </div>
            </div>
          )}
        </div>
      );
    } else if (toolName === 'dharma_search_tool') {
      // Special handling for dharma_search_tool
      const toolReturnData = data as {
        id?: string;
        created_at?: string;
        updated_at?: string;
        message?: string;
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
      
      return (
        <div className="space-y-4">
          {toolReturnData.message && (
            <div className="space-y-1">
              <h5 className="font-medium text-base-custom capitalize text-muted-foreground">Consulta</h5>
              <div className="pl-4">
                <div className="text-base-custom font-medium text-foreground">
                  {toolReturnData.message}
                </div>
              </div>
            </div>
          )}
          
          {toolReturnData.documents && Array.isArray(toolReturnData.documents) && (
            <div className="space-y-1">
              <h5 className="font-medium text-base-custom capitalize text-muted-foreground">Documentos Encontrados ({toolReturnData.documents.length})</h5>
              <div className="pl-4 space-y-3">
                {toolReturnData.documents.map((doc, index) => (
                  <div key={doc.id || index} className="border border-border rounded-lg p-3 space-y-2">
                    <div className="flex justify-between items-start">
                      <h6 className="font-medium text-base-custom text-foreground line-clamp-2">
                        {doc.title}
                      </h6>
                      {doc.collection && (
                        <span className="text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded-md ml-2 shrink-0">
                          {doc.collection}
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground line-clamp-3">
                      {doc.content}
                    </div>
                    {doc.url && (
                      <a 
                        href={doc.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-xs text-primary hover:underline inline-flex items-center gap-1"
                      >
                        Ver documento
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {toolReturnData.metadata?.total_tokens && (
            <div className="space-y-1">
              <h5 className="font-medium text-base-custom capitalize text-muted-foreground">Metadata</h5>
              <div className="pl-4">
                <div className="text-xs text-muted-foreground">
                  Tokens utilizados: {toolReturnData.metadata.total_tokens}
                </div>
              </div>
            </div>
          )}
        </div>
      );
    } else {
      // Default behavior for other tools
      return (
        <div className="space-y-2">
          <div className="text-xs bg-yellow-100 dark:bg-yellow-900/20 p-2 rounded border">
            <strong>Debug Info:</strong> Tool: {toolName || 'unknown'}, Keys: {Object.keys(data).join(', ')}
          </div>
          {Object.entries(data).map(([key, value]) => (
            <div key={key}>
              <p className="font-semibold text-base-custom capitalize">{key.replace(/_/g, ' ')}:</p>
              {key.toLowerCase().includes('text') || key.toLowerCase().includes('markdown') ? (
                <div 
                  className="prose prose-base dark:prose-invert max-w-full prose-base-custom"
                  dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked(String(value)) as string) }}
                />
              ) : (
                <JsonViewer data={value as object} />
              )}
            </div>
          ))}
        </div>
      );
    }
  } catch {
    return (
      <p className="p-2 bg-muted/50 rounded-md text-base-custom whitespace-pre-wrap break-all font-mono">
        {String(toolReturn)}
      </p>
    );
  }
};

export default ToolReturnViewer;
