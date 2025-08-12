'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Send, User, Bot, Loader2, Copy, Lock, Unlock, RefreshCw, Lightbulb, Wrench, LogIn, Search, BarChart2 } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { sendChatMessage, ChatRequestPayload, ChatResponseData, AgentMessage } from '../services/api';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

// Configurar marked para processar quebras de linha
marked.use({ breaks: true });
import { Label } from '@/components/ui/label';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { toast } from 'sonner';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Badge } from '@/components/ui/badge';

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
        instrucoes?: Array<{
          tema?: string;
          instrucoes?: string;
        }>;
      };
      
      return (
        <div className="space-y-4">
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
        </div>
      );
    } else {
      // Default behavior for other tools
      return (
        <div className="space-y-2">
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

const getStepIcon = (messageType: AgentMessage['message_type']) => {
  switch (messageType) {
    case 'reasoning_message': return <Lightbulb className="h-4 w-4 text-yellow-500" />;
    case 'tool_call_message': return <Wrench className="h-4 w-4 text-blue-500" />;
    case 'tool_return_message': return <LogIn className="h-4 w-4 text-green-500" />;
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
      console.log(`Tentativa ${attempt + 1} falhou. Tentando novamente em ${delay}ms...`);
      
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

  return (
    <div className="grid md:grid-cols-[1fr_350px] gap-6 h-full">
      {/* Painel do Chat (Esquerda) */}
      <Card className="flex flex-col h-full overflow-hidden">
        <CardHeader>
          <CardTitle>Chat</CardTitle>
        </CardHeader>
        <CardContent ref={scrollAreaRef} className="flex-1 overflow-y-auto p-4">
            <div className="space-y-4">
              {messages.map((msg, index) => (
                <div key={index} className={`flex items-start gap-3 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
                  {msg.sender === 'bot' && <Bot className="h-6 w-6 text-primary flex-shrink-0" />}
                  <div className={`w-full max-w-[80%] rounded-lg overflow-hidden ${msg.sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                    <div className="relative group">
                      <div
                        className={`prose prose-base dark:prose-invert p-4 pr-12 whitespace-pre-wrap prose-base-custom break-words overflow-wrap-anywhere ${msg.sender === 'user' ? 'text-primary-foreground' : ''}`}
                        dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(msg.content, { breaks: true }) as string) }}
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
        </CardContent>
      </Card>
    </div>
  );
}