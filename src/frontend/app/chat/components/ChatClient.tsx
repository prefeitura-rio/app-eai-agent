'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Send, User, Bot, Loader2, Copy, Lock, Unlock, RefreshCw, Lightbulb, Wrench, LogIn, Search, BarChart2, History, Clock, MessageSquare, Trash2 } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { sendChatMessage, ChatRequestPayload, ChatResponseData, AgentMessage, getUserHistory, HistoryRequestPayload, HistoryMessage, deleteUserHistory, DeleteHistoryRequestPayload } from '../services/api';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

// Configurar marked para processar quebras de linha
marked.use({ breaks: true });
import { Label } from '@/components/ui/label';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { toast } from 'sonner';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';

interface DisplayMessage {
  sender: 'user' | 'bot';
  content: string;
  fullResponse?: ChatResponseData;
}

interface InstrucaoItem {
  tema?: string;
  instrucoes?: string;
}

const JsonViewer = ({ data }: { data: object }) => (
  <pre className="p-2 bg-muted/50 rounded-md text-base-custom whitespace-pre-wrap break-all font-mono">
    {JSON.stringify(data, null, 2)}
  </pre>
);

const ToolReturnViewer = ({ toolReturn, toolName }: { toolReturn: unknown; toolName?: string }) => {
  try {
    const data = typeof toolReturn === 'string' ? JSON.parse(toolReturn) : toolReturn;
    
    // Debug log para verificar a estrutura
    
    if (typeof data !== 'object' || data === null) {
      return <p className="p-2 bg-muted/50 rounded-md text-base-custom whitespace-pre-wrap break-all font-mono">{String(data)}</p>;
    }

    // Special handling for specific tools
    if (toolName === 'google_search') {
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

const getStepIcon = (messageType: AgentMessage['message_type'] | HistoryMessage['message_type']) => {
  switch (messageType) {
    case 'reasoning_message': return <Lightbulb className="h-4 w-4 text-yellow-500" />;
    case 'tool_call_message': return <Wrench className="h-4 w-4 text-blue-500" />;
    case 'tool_return_message': return <LogIn className="h-4 w-4 text-green-500" />;
    case 'user_message': return <User className="h-4 w-4 text-blue-600" />;
    case 'assistant_message': return <Bot className="h-4 w-4 text-green-600" />;
    default: return null;
  }
};

// Função para gerar número aleatório de 9 dígitos
const generateRandomNumber = (): string => {
  return Math.floor(100000000 + Math.random() * 900000000).toString();
};

// Função para copiar texto para clipboard
const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    toast.success("Número copiado para a área de transferência!");
  } catch {
    toast.error("Erro ao copiar número");
  }
};

// Função de retry com backoff exponencial
const retryWithBackoff = async <T,>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000,
  onRetry?: (attempt: number, delay: number) => void
): Promise<T> => {
  let lastError: Error;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      
      // Se é o último tentativa, não espera
      if (attempt === maxRetries) {
        break;
      }
      
      // Calcula delay com backoff exponencial
      const delay = baseDelay * Math.pow(2, attempt);
      
      // Notifica sobre o retry se callback fornecido
      if (onRetry) {
        onRetry(attempt + 1, delay);
      }
      
      // Espera antes da próxima tentativa
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError!;
};

export default function ChatClient() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Estado para controlar se o componente já foi montado no cliente
  const [isMounted, setIsMounted] = useState(false);

  // Chat Parameters State
  const [userNumber, setUserNumber] = useState('');
  const [isNumberFixed, setIsNumberFixed] = useState(false);
  
  // Inicializa os estados após a montagem no cliente
  useEffect(() => {
    setIsMounted(true);
    
    // Recupera o número do localStorage ou gera um novo
    const savedNumber = localStorage.getItem('chat-user-number');
    setUserNumber(savedNumber || generateRandomNumber());
    
    // Recupera o estado do cadeado do localStorage
    const savedFixed = localStorage.getItem('chat-number-fixed') === 'true';
    setIsNumberFixed(savedFixed);
  }, []);
  
  const [provider] = useState('google_agent_engine'); // Provider fixo, não editável

  // History States
  const [historyMessages, setHistoryMessages] = useState<HistoryMessage[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [isDeletingHistory, setIsDeletingHistory] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  
  // History Parameters
  const [sessionTimeoutSeconds, setSessionTimeoutSeconds] = useState(3600); // 1 hora default
  const [useWhatsappFormat, setUseWhatsappFormat] = useState(false);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // Salva o número do usuário no localStorage quando mudar
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('chat-user-number', userNumber);
    }
  }, [userNumber]);

  // Salva o estado do cadeado no localStorage quando mudar
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('chat-number-fixed', isNumberFixed.toString());
    }
  }, [isNumberFixed]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !token) return;

    const userMessage: DisplayMessage = { sender: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const payload: ChatRequestPayload = {
        user_number: userNumber,
        message: input,
        provider: provider,
      };

      // Usa retry com backoff exponencial para lidar com erros de conexão
      const botResponseData = await retryWithBackoff(
        () => sendChatMessage(payload, token),
        3, // maxRetries
        1000, // baseDelay (1 segundo)
        (attempt, delay) => {
          setIsRetrying(true);
          toast.info(`Tentativa ${attempt} falhou. Tentando novamente em ${delay/1000}s...`);
        }
      );
      
      // Limpa o estado de retry se sucesso
      setIsRetrying(false);
      
      const assistantMessage = botResponseData.messages.find(m => m.message_type === 'assistant_message');
      
      const botMessage: DisplayMessage = { 
        sender: 'bot', 
        content: assistantMessage?.content || "Não foi possível obter uma resposta do assistente.",
        fullResponse: botResponseData
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";
      
      // Verifica se é um erro de conexão para mostrar mensagem mais amigável
      const isConnectionError = errorMessage.includes('connection is closed') || 
                               errorMessage.includes('API Error') ||
                               errorMessage.includes('400 Reasoning Engine Execution failed');
      
      const friendlyMessage = isConnectionError 
        ? "Erro de conexão com o serviço. Tente novamente em alguns instantes."
        : `Erro: ${errorMessage}`;
      
      const botErrorMessage: DisplayMessage = { sender: 'bot', content: friendlyMessage };
      setMessages(prev => [...prev, botErrorMessage]);
      
      // Mostra toast informativo para erros de conexão
      if (isConnectionError) {
        toast.error("Erro de conexão. Tentando novamente automaticamente...");
      }
    } finally {
      setIsLoading(false);
      setIsRetrying(false);
      // Retornar foco para o textarea após o envio
      setTimeout(() => {
        textareaRef.current?.focus();
      }, 100);
    }
  };

  const handleGenerateNumber = () => {
    if (!isNumberFixed) {
      const newNumber = generateRandomNumber();
      setUserNumber(newNumber);
      toast.success("Novo número gerado!");
    } else {
      toast.error("Número está travado! Desbloqueie primeiro.");
    }
  };

  const handleToggleFixNumber = () => {
    setIsNumberFixed(!isNumberFixed);
    toast.success(isNumberFixed ? "Número desbloqueado!" : "Número fixado!");
  };

  const handleCopyNumber = () => {
    copyToClipboard(userNumber);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() && !isLoading) {
        handleSendMessage(e as React.FormEvent);
      }
    }
  };

  const handleLoadHistory = async () => {
    if (!token) {
      toast.error("Token de autenticação não encontrado!");
      return;
    }

    setIsLoadingHistory(true);
    setHistoryError(null);

    try {
      const payload: HistoryRequestPayload = {
        user_id: userNumber,
        session_timeout_seconds: sessionTimeoutSeconds,
        use_whatsapp_format: useWhatsappFormat,
      };

      const historyData = await getUserHistory(payload, token);
      setHistoryMessages(historyData.data);
      
      // Limpar chat atual quando carregar histórico
      setMessages([]);
      
      // Filtrar apenas mensagens de conversa (não usage_statistics)
      const conversationMessages = historyData.data.filter(
        msg => msg.message_type !== 'usage_statistics'
      );
      
      toast.success(`Histórico carregado! ${conversationMessages.length} mensagens encontradas.`);
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Erro desconhecido ao carregar histórico.";
      setHistoryError(errorMessage);
      toast.error(`Erro ao carregar histórico: ${errorMessage}`);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleDeleteHistory = async () => {
    if (!token) {
      toast.error("Token de autenticação não encontrado!");
      return;
    }

    setIsDeletingHistory(true);
    setHistoryError(null);
    setShowDeleteModal(false); // Fechar o modal

    try {
      const payload: DeleteHistoryRequestPayload = {
        user_id: userNumber,
      };

      const deleteResult = await deleteUserHistory(payload, token);
      
      // Limpar histórico carregado e chat atual
      setHistoryMessages([]);
      setMessages([]);
      
      // Calcular total de linhas deletadas
      const totalDeleted = (deleteResult.tables.checkpoints.deleted_rows || 0) + 
                          (deleteResult.tables.checkpoints_writes.deleted_rows || 0);
      
      if (deleteResult.overall_result === "success") {
        toast.success(`Histórico deletado com sucesso! ${totalDeleted} registros removidos.`);
      } else {
        toast.warning(`Operação parcial: ${totalDeleted} registros removidos. Verifique os detalhes.`);
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Erro desconhecido ao deletar histórico.";
      setHistoryError(errorMessage);
      toast.error(`Erro ao deletar histórico: ${errorMessage}`);
    } finally {
      setIsDeletingHistory(false);
    }
  };

  return (
    <div className="grid md:grid-cols-[1fr_350px] gap-6 h-full">
      {/* Painel do Chat (Esquerda) */}
      <Card className="flex flex-col h-full overflow-hidden">
        <CardHeader>
          <CardTitle>Chat</CardTitle>
        </CardHeader>
        <CardContent ref={scrollAreaRef} className="flex-1 overflow-y-auto p-4">
            <div className="space-y-4">
              {/* Mensagens do Histórico */}
              {(() => {
                // Filtrar mensagens de conversa
                const conversationMessages = historyMessages.filter(msg => 
                  msg.message_type === 'user_message' || msg.message_type === 'assistant_message'
                );
                
                if (conversationMessages.length === 0) return null;

                // Criar mapeamento de session_id para número sequencial
                const uniqueSessionIds = Array.from(new Set(
                  conversationMessages.map(msg => msg.session_id).filter(Boolean)
                ));
                const sessionIdToNumber = Object.fromEntries(
                  uniqueSessionIds.map((sessionId, index) => [sessionId, index + 1])
                );

                // Agrupar mensagens por sessão
                const groupedBySessions = uniqueSessionIds.map(sessionId => ({
                  sessionId,
                  sessionNumber: sessionIdToNumber[sessionId || ''],
                  messages: conversationMessages.filter(msg => msg.session_id === sessionId)
                }));

                return groupedBySessions.map((session) => (
                  <div key={`session-${session.sessionId}`}>
                    {/* Separador da Sessão */}
                    <div className="flex items-center gap-4 py-4">
                      <div className="flex-1 border-t border-border"></div>
                      <div className="flex items-center gap-2 px-3 py-1 bg-muted/50 rounded-full border">
                        <History className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium text-muted-foreground">Sessão {session.sessionNumber}</span>
                      </div>
                      <div className="flex-1 border-t border-border"></div>
                    </div>
                    
                    {/* Mensagens da Sessão */}
                    <div className="space-y-4">
                      {session.messages.map((msg, msgIndex) => (
                        <div key={`history-${msg.id}-${msgIndex}`} className={`flex items-start gap-3 ${msg.message_type === 'user_message' ? 'justify-end' : ''}`}>
                    {msg.message_type === 'assistant_message' && <Bot className="h-6 w-6 text-primary flex-shrink-0" />}
                    <div className={`w-full max-w-[80%] rounded-lg overflow-hidden ${msg.message_type === 'user_message' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                      <div className="relative group">
                        <div className="flex items-center gap-2 px-3 py-1 bg-black/10 border-b border-border/20">
                          <History className="h-3 w-3" />
                          <span className="text-xs font-mono">
                            Sessão {sessionIdToNumber[msg.session_id || '']} • {new Date(msg.date).toLocaleDateString('pt-BR')} {new Date(msg.date).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                          </span>
                          {msg.time_since_last_message && (
                            <span className="text-xs text-muted-foreground">
                              +{Math.round(msg.time_since_last_message)}s
                            </span>
                          )}
                        </div>
                      <div
                        className={`prose prose-base dark:prose-invert p-4 pr-12 whitespace-pre-wrap prose-base-custom break-words overflow-wrap-anywhere ${msg.message_type === 'user_message' ? 'text-primary-foreground' : ''}`}
                        style={{
                          '--tw-prose-pre-bg': 'rgb(31 41 55)',
                          '--tw-prose-pre-code': 'rgb(209 213 219)',
                        } as React.CSSProperties}
                        dangerouslySetInnerHTML={{ 
                          __html: (() => {
                            const content = msg.content || '';
                            const parsed = marked.parse(content, { breaks: true }) as string;
                            
                            // Adicionar estilos inline para blocos de código com a mesma cor de fundo da mensagem
                            const isUserMessage = msg.message_type === 'user_message';
                            const codeTextColor = isUserMessage ? 'rgb(255, 255, 255)' : 'inherit';
                            
                            const styledHTML = parsed.replace(
                              /<pre><code class="language-json">/g,
                              `<pre style="background-color: transparent; padding: 1rem; border-radius: 0; overflow-x: auto; white-space: pre-wrap; word-break: break-all; margin: 0;"><code class="language-json" style="color: ${codeTextColor}; font-family: ui-monospace, SFMono-Regular, Consolas, monospace;">`
                            );
                            
                            return DOMPurify.sanitize(styledHTML);
                          })()
                        }}
                      />
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              variant="ghost"
                              size="sm"
                              className={`absolute top-8 right-2 border ${
                                msg.message_type === 'user_message' 
                                  ? 'bg-white/20 hover:bg-white/30 border-white/30 hover:border-white/40 text-white' 
                                  : 'bg-primary/10 hover:bg-primary/20 border-primary/20 hover:border-primary/30 text-primary'
                              }`}
                              onClick={() => copyToClipboard(msg.content || '')}
                            >
                              <Copy className="h-3 w-3" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Copiar mensagem do histórico</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                    {msg.message_type === 'assistant_message' && (
                      <div className="mt-3 pt-3 border-t border-muted/30">
                        <Accordion type="single" collapsible className="w-full">
                          <AccordionItem value={`history-details-${msg.id}`} className="border-none">
                            <AccordionTrigger className="px-3 py-2 text-sm font-medium bg-background/50 hover:bg-background/80 rounded-md border border-border hover:border-border/80 transition-colors">
                              <div className="flex items-center gap-2">
                                <Search className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                                <span className="text-blue-600 dark:text-blue-400">Ver Detalhes (Histórico)</span>
                              </div>
                            </AccordionTrigger>
                            <AccordionContent className="p-4 space-y-4">
                              {/* Buscar todas as mensagens da interação (entre user_message anterior e próxima user_message) */}
                              {(() => {
                                // Encontrar o índice da mensagem atual na lista completa
                                const currentIndex = historyMessages.findIndex(m => m.id === msg.id);
                                
                                if (currentIndex === -1) return null;
                                
                                // Procurar a user_message que inicia esta interação (indo para trás)
                                let interactionStart = currentIndex;
                                while (interactionStart > 0) {
                                  interactionStart--;
                                  if (historyMessages[interactionStart].message_type === 'user_message') {
                                    break;
                                  }
                                }
                                
                                // Se não encontrou uma user_message antes, usar o início
                                if (historyMessages[interactionStart].message_type !== 'user_message') {
                                  return null;
                                }
                                
                                // Procurar a próxima user_message para definir o fim da interação (indo para frente)
                                let interactionEnd = currentIndex;
                                while (interactionEnd < historyMessages.length - 1) {
                                  interactionEnd++;
                                  if (historyMessages[interactionEnd].message_type === 'user_message') {
                                    interactionEnd--; // Não incluir a próxima user_message
                                    break;
                                  }
                                }
                                
                                // Extrair todas as mensagens da interação
                                const interactionMessages = historyMessages.slice(interactionStart, interactionEnd + 1);
                                
                                // Filtrar apenas os steps (não user e não assistant final)
                                const interactionSteps = interactionMessages.filter(step => 
                                  step.message_type !== 'usage_statistics' &&
                                  step.message_type !== 'user_message' &&
                                  step.id !== msg.id && // Não incluir a própria mensagem assistant atual
                                  (step.message_type === 'tool_call_message' || 
                                   step.message_type === 'tool_return_message' ||
                                   step.message_type === 'reasoning_message' ||
                                   step.message_type === 'assistant_message')
                                );
                                
                                return (
                                  <div className="space-y-2">
                                    {interactionSteps.length > 0 ? (
                                      interactionSteps.map((step, stepIndex) => (
                                        <div key={`step-${step.id}-${stepIndex}`} className="space-y-2 border-l-2 border-muted pl-3">
                                          <div className="flex items-center gap-2">
                                            {getStepIcon(step.message_type)}
                                            <h5 className="font-semibold text-sm">{step.message_type.replace(/_/g, ' ')}</h5>
                                            {step.name && <Badge variant="secondary">{step.name}</Badge>}
                                          </div>
                                          {step.reasoning && (
                                            <p className="italic text-muted-foreground text-sm">{step.reasoning}</p>
                                          )}
                                          {step.tool_call && (
                                            <div>
                                              <p className="font-semibold text-sm capitalize mb-2">Tool Call Arguments:</p>
                                              <JsonViewer data={(() => {
                                                try {
                                                  return typeof step.tool_call.arguments === 'string' 
                                                    ? JSON.parse(step.tool_call.arguments)
                                                    : step.tool_call.arguments;
                                                } catch {
                                                  return { raw: step.tool_call.arguments };
                                                }
                                              })()} />
                                            </div>
                                          )}
                                          {step.tool_return && (
                                            <ToolReturnViewer toolReturn={step.tool_return} toolName={step.name || undefined} />
                                          )}
                                          {step.content && step.message_type === 'assistant_message' && (
                                            <div>
                                              <p className="font-semibold text-sm capitalize mb-2">Resposta Intermediária:</p>
                                              <div 
                                                className="prose prose-sm dark:prose-invert max-w-none bg-muted/30 p-2 rounded"
                                                dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(step.content, { breaks: true }) as string) }}
                                              />
                                            </div>
                                          )}
                                        </div>
                                      ))
                                    ) : (
                                      <div className="text-sm text-muted-foreground italic">
                                        Resposta direta sem uso de ferramentas
                                      </div>
                                    )}
                                  </div>
                                );
                              })()}
                              
                              <div className="space-y-2 pt-2 border-t">
                                <h4 className="font-semibold">Informações da Mensagem</h4>
                                <div className="text-sm space-y-1">
                                  <div><span className="font-medium">ID:</span> {msg.id}</div>
                                  <div><span className="font-medium">Session ID:</span> {msg.session_id}</div>
                                  <div><span className="font-medium">Data:</span> {new Date(msg.date).toLocaleString('pt-BR')}</div>
                                  <div><span className="font-medium">Tipo:</span> {msg.message_type}</div>
                                  {msg.time_since_last_message && (
                                    <div><span className="font-medium">Tempo desde última:</span> {Math.round(msg.time_since_last_message)}s</div>
                                  )}
                                  {msg.model_name && (
                                    <div><span className="font-medium">Modelo:</span> {msg.model_name}</div>
                                  )}
                                  {msg.finish_reason && (
                                    <div><span className="font-medium">Finish Reason:</span> {msg.finish_reason}</div>
                                  )}
                                </div>
                              </div>
                              
                              {msg.usage_metadata && (
                                <div className="space-y-2 pt-2 border-t">
                                  <div className="flex items-center gap-2">
                                    <BarChart2 className="h-4 w-4 text-purple-500" />
                                    <h4 className="font-semibold">Usage Metadata</h4>
                                  </div>
                                  <JsonViewer data={msg.usage_metadata} />
                                </div>
                              )}
                            </AccordionContent>
                          </AccordionItem>
                        </Accordion>
                      </div>
                    )}
                          </div>
                          {msg.message_type === 'user_message' && <User className="h-6 w-6 flex-shrink-0" />}
                        </div>
                      ))}
                    </div>
                  </div>
                ));
              })()}

              {/* Separador entre histórico e chat atual */}
              {historyMessages.length > 0 && messages.length > 0 && (
                <div className="flex items-center gap-4 py-4">
                  <div className="flex-1 border-t border-border"></div>
                  <div className="flex items-center gap-2 px-3 py-1 bg-primary/10 rounded-full border">
                    <MessageSquare className="h-4 w-4 text-primary" />
                    <span className="text-sm font-medium text-primary">Nova Conversa</span>
                  </div>
                  <div className="flex-1 border-t border-border"></div>
                </div>
              )}

              {/* Mensagens do Chat Atual */}
              {messages.map((msg, index) => (
                <div key={index} className={`flex items-start gap-3 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
                  {msg.sender === 'bot' && <Bot className="h-6 w-6 text-primary flex-shrink-0" />}
                  <div className={`w-full max-w-[80%] rounded-lg overflow-hidden ${msg.sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                    <div className="relative group">
                      <div
                        className={`prose prose-base dark:prose-invert p-4 pr-12 whitespace-pre-wrap prose-base-custom break-words overflow-wrap-anywhere ${msg.sender === 'user' ? 'text-primary-foreground' : ''}`}
                        dangerouslySetInnerHTML={{ 
                          __html: (() => {
                            const content = msg.content;
                            const parsed = marked.parse(content, { breaks: true }) as string;
                            
                            // Adicionar estilos inline para blocos de código com a mesma cor de fundo da mensagem
                            const isUserMessage = msg.sender === 'user';
                            const codeTextColor = isUserMessage ? 'rgb(255, 255, 255)' : 'inherit';
                            
                            const styledHTML = parsed.replace(
                              /<pre><code class="language-json">/g,
                              `<pre style="background-color: transparent; padding: 1rem; border-radius: 0; overflow-x: auto; white-space: pre-wrap; word-break: break-all; margin: 0;"><code class="language-json" style="color: ${codeTextColor}; font-family: ui-monospace, SFMono-Regular, Consolas, monospace;">`
                            );
                            
                            return DOMPurify.sanitize(styledHTML);
                          })()
                        }}
                      />
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              variant="ghost"
                              size="sm"
                              className={`absolute top-2 right-2 border ${
                                msg.sender === 'user' 
                                  ? 'bg-white/20 hover:bg-white/30 border-white/30 hover:border-white/40 text-white' 
                                  : 'bg-primary/10 hover:bg-primary/20 border-primary/20 hover:border-primary/30 text-primary'
                              }`}
                              onClick={() => copyToClipboard(msg.content)}
                            >
                              <Copy className="h-3 w-3" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Copiar mensagem</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                    {msg.sender === 'bot' && msg.fullResponse && (
                      <div className="mt-3 pt-3 border-t border-muted/30">
                        <Accordion type="single" collapsible className="w-full">
                          <AccordionItem value="item-1" className="border-none">
                            <AccordionTrigger className="px-3 py-2 text-sm font-medium bg-background/50 hover:bg-background/80 rounded-md border border-border hover:border-border/80 transition-colors">
                              <div className="flex items-center gap-2">
                                <Search className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                                <span className="text-blue-600 dark:text-blue-400">Ver Detalhes</span>
                              </div>
                            </AccordionTrigger>
                          <AccordionContent className="p-4 space-y-4">
                            {msg.fullResponse.messages.filter(m => m.message_type !== 'assistant_message').map((step, stepIndex) => (
                              <div key={`${step.id}-${step.message_type}-${stepIndex}`} className="space-y-2">
                                <div className="flex items-center gap-2">
                                  {getStepIcon(step.message_type)}
                                  <h4 className="font-semibold">{step.message_type.replace(/_/g, ' ')}</h4>
                                  {step.name && <Badge variant="secondary">{step.name}</Badge>}
                                </div>
                                {step.reasoning && <p className="italic text-muted-foreground text-base pl-6">{step.reasoning}</p>}
                                {step.tool_call && (
                                  <div>
                                    <p className="font-semibold text-base capitalize mb-2">Tool Call Arguments:</p>
                                    <JsonViewer data={(() => {
                                      try {
                                        return typeof step.tool_call.arguments === 'string' 
                                          ? JSON.parse(step.tool_call.arguments)
                                          : step.tool_call.arguments;
                                      } catch {
                                        return { raw: step.tool_call.arguments };
                                      }
                                    })()} />
                                  </div>
                                )}
                                {step.tool_return && <ToolReturnViewer toolReturn={step.tool_return} toolName={step.name || undefined} />}
                              </div>
                            ))}
                            <div className="space-y-2 pt-2 border-t">
                                <div className="flex items-center gap-2">
                                  <BarChart2 className="h-4 w-4 text-purple-500" />
                                  <h4 className="font-semibold">Usage Statistics</h4>
                                </div>
                                <JsonViewer data={msg.fullResponse.usage} />
                            </div>
                          </AccordionContent>
                        </AccordionItem>
                      </Accordion>
                    </div>
                  )}
                  </div>
                  {msg.sender === 'user' && <User className="h-6 w-6 flex-shrink-0" />}
                </div>
              ))}
            </div>
        </CardContent>
        <CardFooter className="border-t pt-4">
          <form onSubmit={handleSendMessage} className="flex w-full items-center space-x-2">
            <Textarea
              ref={textareaRef}
              id="message"
              placeholder="Digite sua mensagem..."
              className="flex-1 min-h-[60px] resize-none"
              autoComplete="off"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              rows={3}
              style={{ resize: 'none' }}
            />
            <Button type="submit" size="icon" disabled={isLoading}>
              {isLoading ? (
                isRetrying ? (
                  <div className="flex items-center gap-1">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    <span className="text-xs">Retry</span>
                  </div>
                ) : (
                  <Loader2 className="h-4 w-4 animate-spin" />
                )
              ) : (
                <Send className="h-4 w-4" />
              )}
              <span className="sr-only">Enviar</span>
            </Button>
          </form>
        </CardFooter>
      </Card>

      {/* Painel de Parâmetros (Direita) */}
      <Card className="flex flex-col h-full">
        <CardHeader>
          <CardTitle>Parâmetros</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto space-y-4">
          <div className="space-y-2">
            <Label htmlFor="user-number">User Number</Label>
            <div className="flex items-center space-x-2">
              <Input
                id="user-number"
                value={isMounted ? userNumber : ''}
                onChange={(e) => !isNumberFixed && setUserNumber(e.target.value)}
                disabled={isNumberFixed}
                className="flex-1"
              />
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button 
                      variant="outline" 
                      size="icon" 
                      onClick={handleGenerateNumber}
                      disabled={isNumberFixed || !isMounted}
                    >
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Gerar novo número aleatório</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button 
                      variant="outline" 
                      size="icon" 
                      onClick={handleToggleFixNumber}
                      disabled={!isMounted}
                    >
                      {isNumberFixed ? <Lock className="h-4 w-4" /> : <Unlock className="h-4 w-4" />}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{isNumberFixed ? "Desbloquear número" : "Fixar número"}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button 
                      variant="outline" 
                      size="icon" 
                      onClick={handleCopyNumber}
                      disabled={!isMounted}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Copiar número</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="provider">Provider</Label>
            <Input
              id="provider"
              value={provider}
              disabled
              className="bg-muted"
            />
          </div>

          <Separator className="my-4" />

          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <History className="h-4 w-4 text-primary" />
              <h3 className="font-semibold text-sm">Histórico</h3>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="session-timeout">Session Timeout (segundos)</Label>
              <Input
                id="session-timeout"
                type="number"
                value={sessionTimeoutSeconds}
                onChange={(e) => setSessionTimeoutSeconds(parseInt(e.target.value) || 3600)}
                min="60"
                max="86400"
                placeholder="3600"
              />
              <p className="text-xs text-muted-foreground">
                Tempo limite para agrupar mensagens na mesma sessão
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="whatsapp-format"
                checked={useWhatsappFormat}
                onCheckedChange={(checked) => setUseWhatsappFormat(checked as boolean)}
              />
              <Label htmlFor="whatsapp-format" className="text-sm">
                Formato WhatsApp
              </Label>
            </div>

            <Button
              onClick={handleLoadHistory}
              disabled={isLoadingHistory || !isMounted}
              className="w-full"
              variant="outline"
            >
              {isLoadingHistory ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Carregando...
                </>
              ) : (
                <>
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Carregar Histórico
                </>
              )}
            </Button>

            <Dialog open={showDeleteModal} onOpenChange={setShowDeleteModal}>
              <DialogTrigger asChild>
                <Button
                  disabled={isDeletingHistory || isLoadingHistory || !isMounted}
                  className="w-full"
                  variant="destructive"
                >
                  {isDeletingHistory ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Deletando...
                    </>
                  ) : (
                    <>
                      <Trash2 className="h-4 w-4 mr-2" />
                      Deletar Histórico
                    </>
                  )}
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2 text-destructive">
                    <Trash2 className="h-5 w-5" />
                    Deletar Histórico
                  </DialogTitle>
                  <DialogDescription className="text-base">
                    Tem certeza que deseja deletar <strong>PERMANENTEMENTE</strong> todo o histórico do usuário <code className="bg-muted px-1 py-0.5 rounded text-sm font-mono">{userNumber}</code>?
                  </DialogDescription>
                </DialogHeader>
                
                <div className="py-4">
                  <div className="flex items-start gap-3 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                    <div className="text-destructive mt-0.5">⚠️</div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-destructive mb-1">Atenção!</h4>
                      <ul className="text-sm text-destructive/80 space-y-1">
                        <li>• Esta ação não pode ser desfeita</li>
                        <li>• Todos os checkpoints serão removidos</li>
                        <li>• O histórico será perdido permanentemente</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <DialogFooter className="gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowDeleteModal(false)}
                    disabled={isDeletingHistory}
                  >
                    Cancelar
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={handleDeleteHistory}
                    disabled={isDeletingHistory}
                  >
                    {isDeletingHistory ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Deletando...
                      </>
                    ) : (
                      <>
                        <Trash2 className="h-4 w-4 mr-2" />
                        Sim, Deletar
                      </>
                    )}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {historyError && (
              <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
                <p className="text-sm text-destructive">{historyError}</p>
              </div>
            )}

            {historyMessages.length > 0 && (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium text-green-600">
                    {historyMessages.filter(m => m.message_type !== 'usage_statistics').length} mensagens carregadas
                  </span>
                </div>
                <Button
                  onClick={() => {
                    setHistoryMessages([]);
                    setMessages([]);
                    setHistoryError(null);
                    toast.info("Histórico e chat atual limpos!");
                  }}
                  size="sm"
                  variant="ghost"
                  className="h-6 px-2 text-xs"
                >
                  Limpar Tudo
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}