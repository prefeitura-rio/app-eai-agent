'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Send, User, Bot, Loader2, Trash2, Lightbulb, Wrench, LogIn, BarChart2 } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { sendChatMessage, ChatRequestPayload, deleteAgentAssociation, ChatResponseData, AgentMessage } from '../services/api';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { toast } from 'sonner';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Badge } from '@/components/ui/badge';

interface DisplayMessage {
  sender: 'user' | 'bot';
  content: string;
  fullResponse?: ChatResponseData;
}

const JsonViewer = ({ data }: { data: object }) => (
  <pre className="p-2 bg-muted/50 rounded-md text-xs whitespace-pre-wrap break-all font-mono">
    {JSON.stringify(data, null, 2)}
  </pre>
);

const ToolReturnViewer = ({ toolReturn }: { toolReturn: any }) => {
  try {
    const data = typeof toolReturn === 'string' ? JSON.parse(toolReturn) : toolReturn;
    
    // Se não for um objeto, renderiza como string simples
    if (typeof data !== 'object' || data === null) {
      return <p className="p-2 bg-muted/50 rounded-md text-xs whitespace-pre-wrap break-all font-mono">{String(data)}</p>;
    }

    return (
      <div className="space-y-2">
        {Object.entries(data).map(([key, value]) => (
          <div key={key}>
            <p className="font-semibold text-xs capitalize">{key.replace(/_/g, ' ')}:</p>
            {key.toLowerCase().includes('text') || key.toLowerCase().includes('markdown') ? (
              <div 
                className="prose prose-sm dark:prose-invert max-w-full"
                dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked(String(value)) as string) }}
              />
            ) : (
              <JsonViewer data={value as object} />
            )}
          </div>
        ))}
      </div>
    );
  } catch (error) {
    // Se o parsing falhar, renderiza como texto simples
    return (
      <p className="p-2 bg-muted/50 rounded-md text-xs whitespace-pre-wrap break-all font-mono">
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

export default function ChatClient() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Agent Parameters State
  const [userNumber, setUserNumber] = useState('chat-ui-user');
  const [systemPrompt, setSystemPrompt] = useState('You are a helpful AI assistant.');
  const [model, setModel] = useState('google_ai/gemini-2.5-flash-lite-preview-06-17');
  const [tools, setTools] = useState('google_search, equipments_instructions, equipments_by_address');

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

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
        name: `ui-agent-${userNumber}`,
        system: systemPrompt,
        model: model,
        tools: tools.split(',').map(t => t.trim()).filter(Boolean),
      };

      const botResponseData = await sendChatMessage(payload, token);
      const assistantMessage = botResponseData.messages.find(m => m.message_type === 'assistant_message');
      
      const botMessage: DisplayMessage = { 
        sender: 'bot', 
        content: assistantMessage?.content || "Não foi possível obter uma resposta do assistente.",
        fullResponse: botResponseData
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";
      const botErrorMessage: DisplayMessage = { sender: 'bot', content: `Error: ${errorMessage}` };
      setMessages(prev => [...prev, botErrorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAgent = async () => {
    if (!userNumber.trim() || !token) {
      toast.error("User Number é obrigatório para deletar um agente.");
      return;
    }
    if (confirm(`Tem certeza que deseja deletar o agente para o usuário "${userNumber}"? A conversa será reiniciada.`)) {
      const result = await deleteAgentAssociation(userNumber, token);
      if (result.success) {
        toast.success("Agente deletado com sucesso. A próxima mensagem criará um novo agente.");
        setMessages([]); // Clear chat history
      } else {
        toast.error("Erro ao deletar agente", { description: result.message });
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
                  <div className={`w-full max-w-[80%] rounded-lg ${msg.sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                    <div 
                      className="prose prose-sm dark:prose-invert p-4"
                      dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked(msg.content) as string) }}
                    />
                    {msg.sender === 'bot' && msg.fullResponse && (
                      <Accordion type="single" collapsible className="w-full bg-background/50 rounded-b-lg">
                        <AccordionItem value="item-1" className="border-x-0 border-b-0">
                          <AccordionTrigger className="px-4 py-2 text-xs">Ver Detalhes</AccordionTrigger>
                          <AccordionContent className="p-4 space-y-4">
                            {msg.fullResponse.messages.filter(m => m.message_type !== 'assistant_message').map((step, stepIndex) => (
                              <div key={`${step.id}-${step.message_type}-${stepIndex}`} className="space-y-2">
                                <div className="flex items-center gap-2">
                                  {getStepIcon(step.message_type)}
                                  <h4 className="font-semibold">{step.message_type.replace(/_/g, ' ')}</h4>
                                  {step.name && <Badge variant="secondary">{step.name}</Badge>}
                                </div>
                                {step.reasoning && <p className="italic text-muted-foreground text-xs pl-6">"{step.reasoning}"</p>}
                                {step.tool_call && <JsonViewer data={JSON.parse(step.tool_call.arguments)} />}
                                {step.tool_return && <ToolReturnViewer toolReturn={step.tool_return} />}
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
                    )}
                  </div>
                  {msg.sender === 'user' && <User className="h-6 w-6 flex-shrink-0" />}
                </div>
              ))}
            </div>
        </CardContent>
        <CardFooter className="border-t pt-4">
          <form onSubmit={handleSendMessage} className="flex w-full items-center space-x-2">
            <Input
              id="message"
              placeholder="Digite sua mensagem..."
              className="flex-1"
              autoComplete="off"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <Button type="submit" size="icon" disabled={isLoading}>
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
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
                value={userNumber}
                onChange={(e) => setUserNumber(e.target.value)}
              />
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="outline" size="icon" onClick={handleDeleteAgent}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Deletar agente e reiniciar conversa</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="system-prompt">System Prompt</Label>
            <Textarea
              id="system-prompt"
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              className="h-32"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="model">Modelo</Label>
            <Textarea
              id="model"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="h-10 resize-y"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="tools">Tools (separado por vírgula)</Label>
            <Textarea
              id="tools"
              value={tools}
              onChange={(e) => setTools(e.target.value)}
              className="h-20 resize-y"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}