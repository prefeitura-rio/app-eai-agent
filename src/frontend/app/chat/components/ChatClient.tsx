'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MessageSquare, History } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { sendChatMessage, ChatRequestPayload, getUserHistory, HistoryRequestPayload, HistoryMessage, deleteUserHistory, DeleteHistoryRequestPayload, AgentMessage } from '../services/api';
import { marked } from 'marked';
import { toast } from 'sonner';

import { DisplayMessage } from '../types/chat';

// Modules
import ChatSidebar from './modules/ChatSidebar';
import ChatInput from './modules/ChatInput';
import JsonViewer from './modules/JsonViewer';
import ToolReturnViewer from './modules/ToolReturnViewer';
import { Bot, User, Copy, Search, BarChart2, Lightbulb, Wrench, LogIn, Clock } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Button } from '@/components/ui/button';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import DOMPurify from 'dompurify';

// Configurar marked para processar quebras de linha
marked.use({ breaks: true });

// --- Utils ---

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

const generateRandomNumber = (): string => {
  return Math.floor(100000000 + Math.random() * 900000000).toString();
};

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    toast.success("Copiado para a área de transferência!");
  } catch {
    toast.error("Erro ao copiar");
  }
};

// --- Main Component ---

export default function ChatClient() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
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
  const [reasoningEngineId, setReasoningEngineId] = useState('');

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
  }, [messages, historyMessages]);

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

  const [requestStartTime, setRequestStartTime] = useState<number | null>(null);
  const isSendingRef = useRef(false);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Verificação síncrona para evitar envios duplicados rápidos
    if (isSendingRef.current) return;
    if (!input.trim() || !token) return;

    isSendingRef.current = true;
    const startTime = Date.now();
    setRequestStartTime(startTime);
    
    const userMessage: DisplayMessage = { 
      sender: 'user', 
      content: input,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const payload: ChatRequestPayload = {
        user_number: userNumber,
        message: input,
        provider: provider,
        ...(reasoningEngineId && { reasoning_engine_id: reasoningEngineId }),
      };

      // Chamada direta sem retry automático
      const botResponseData = await sendChatMessage(payload, token);
      
      const latency = (Date.now() - startTime) / 1000;
      const assistantMessage = botResponseData.messages.find(m => m.message_type === 'assistant_message');
      
      const botMessage: DisplayMessage = { 
        sender: 'bot', 
        content: assistantMessage?.content || "Não foi possível obter uma resposta do assistente.",
        fullResponse: botResponseData,
        timestamp: new Date().toISOString(),
        latency: latency
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";

      const isConnectionError = errorMessage.includes('connection is closed') ||
                               errorMessage.includes('Failed to fetch') ||
                               errorMessage.includes('NetworkError');
      
      const isTimeout = errorMessage.includes('Timeout') || errorMessage.includes('504');

      if (isTimeout || isConnectionError) {
         // Silenciosamente falha no chat, apenas avisa via toast se necessário
         // O usuário pediu para não mostrar msg de erro no chat para não confundir
         console.warn("Timeout ou erro de conexão:", errorMessage);
      } else {
         toast.error("Erro ao enviar mensagem.");
         // Opcional: Adicionar msg de erro no chat apenas para erros fatais não-timeout
         // const botErrorMessage: DisplayMessage = { sender: 'bot', content: `Erro: ${errorMessage}` };
         // setMessages(prev => [...prev, botErrorMessage]);
      }

    } finally {
      setIsLoading(false);
      setRequestStartTime(null);
      isSendingRef.current = false;
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
      // Limpar histórico e mensagens atuais
      setHistoryMessages([]);
      setMessages([]);
      toast.success("Novo número gerado e tela limpa!");
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
    setShowDeleteModal(false);

    try {
      const payload: DeleteHistoryRequestPayload = {
        user_id: userNumber,
      };

      const deleteResult = await deleteUserHistory(payload, token);
      
      // Limpar histórico carregado e chat atual
      setHistoryMessages([]);
      setMessages([]);
      
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

  // Helper to render message content
  const renderMessageContent = (content: string, isUser: boolean) => {
    const parsed = marked.parse(content || '', { breaks: true }) as string;
    const codeTextColor = isUser ? 'rgb(255, 255, 255)' : 'inherit';
    
    const styledHTML = parsed.replace(
      /<pre><code class="language-json">/g,
      `<pre style="background-color: transparent; padding: 1rem; border-radius: 0; overflow-x: auto; white-space: pre-wrap; word-break: break-all; margin: 0;"><code class="language-json" style="color: ${codeTextColor}; font-family: ui-monospace, SFMono-Regular, Consolas, monospace;">`
    );
    
    return (
      <div
        className={`prose prose-base dark:prose-invert p-4 pr-12 whitespace-pre-wrap prose-base-custom break-words overflow-wrap-anywhere ${isUser ? 'text-primary-foreground' : ''}`}
        style={{
          '--tw-prose-pre-bg': 'rgb(31 41 55)',
          '--tw-prose-pre-code': 'rgb(209 213 219)',
        } as React.CSSProperties}
        dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(styledHTML) }}
      />
    );
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
                      
                      {renderMessageContent(msg.content || '', msg.message_type === 'user_message')}

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
                              {/* Buscar todas as mensagens da interação */}
                              {(() => {
                                const currentIndex = historyMessages.findIndex(m => m.id === msg.id);
                                if (currentIndex === -1) return null;
                                
                                let interactionStart = currentIndex;
                                while (interactionStart > 0) {
                                  interactionStart--;
                                  if (historyMessages[interactionStart].message_type === 'user_message') {
                                    break;
                                  }
                                }
                                
                                if (historyMessages[interactionStart].message_type !== 'user_message') {
                                  return null;
                                }
                                
                                let interactionEnd = currentIndex;
                                while (interactionEnd < historyMessages.length - 1) {
                                  interactionEnd++;
                                  if (historyMessages[interactionEnd].message_type === 'user_message') {
                                    interactionEnd--;
                                    break;
                                  }
                                }
                                
                                const interactionMessages = historyMessages.slice(interactionStart, interactionEnd + 1);
                                
                                const interactionSteps = interactionMessages.filter(step => 
                                  step.message_type !== 'usage_statistics' &&
                                  step.message_type !== 'user_message' &&
                                  step.id !== msg.id &&
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
                      
                      <div className="flex items-center gap-2 px-3 py-1 bg-black/10 border-b border-border/20">
                        <Clock className="h-3 w-3" />
                        {msg.timestamp && (
                          <span className="text-xs font-mono opacity-80">
                            {new Date(msg.timestamp).toLocaleDateString('pt-BR')} {new Date(msg.timestamp).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                          </span>
                        )}
                        {msg.latency && (
                          <span className="text-xs text-muted-foreground font-mono">
                            +{msg.latency.toFixed(1)}s
                          </span>
                        )}
                      </div>

                      {renderMessageContent(msg.content || '', msg.sender === 'user')}
                      
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              variant="ghost"
                              size="sm"
                              className={`absolute top-8 right-2 border ${
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
        
        <ChatInput 
          input={input}
          setInput={setInput}
          isLoading={isLoading}
          requestStartTime={requestStartTime}
          onSendMessage={handleSendMessage}
          textareaRef={textareaRef}
        />
      </Card>

      {/* Painel de Parâmetros (Direita) */}
      <ChatSidebar
        userNumber={userNumber}
        setUserNumber={setUserNumber}
        isNumberFixed={isNumberFixed}
        isMounted={isMounted}
        provider={provider}
        reasoningEngineId={reasoningEngineId}
        setReasoningEngineId={setReasoningEngineId}
        sessionTimeoutSeconds={sessionTimeoutSeconds}
        setSessionTimeoutSeconds={setSessionTimeoutSeconds}
        useWhatsappFormat={useWhatsappFormat}
        setUseWhatsappFormat={setUseWhatsappFormat}
        isLoadingHistory={isLoadingHistory}
        isDeletingHistory={isDeletingHistory}
        historyMessages={historyMessages}
        historyError={historyError}
        showDeleteModal={showDeleteModal}
        setShowDeleteModal={setShowDeleteModal}
        onGenerateNumber={handleGenerateNumber}
        onToggleFixNumber={handleToggleFixNumber}
        onCopyNumber={handleCopyNumber}
        onLoadHistory={handleLoadHistory}
        onClearScreen={() => {
          setHistoryMessages([]);
          setMessages([]);
          setHistoryError(null);
          toast.info("Tela limpa!");
        }}
        onDeleteHistory={handleDeleteHistory}
      />
    </div>
  );
}
