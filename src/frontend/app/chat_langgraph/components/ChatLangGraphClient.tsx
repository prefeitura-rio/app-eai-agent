'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Send, User, Bot, Loader2, BookText } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { sendChatMessage, ChatRequestPayload, LangGraphChatResponse, AgentConfig } from '../services/api';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

interface DisplayMessage {
  sender: 'user' | 'bot';
  content: string;
  fullResponse?: LangGraphChatResponse;
}

const JsonViewer = ({ data }: { data: object | string }) => {
    const content = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
    return (
        <pre className="p-2 bg-muted/50 rounded-md text-xs whitespace-pre-wrap break-all font-mono">
            {content}
        </pre>
    );
};


export default function ChatLangGraphClient() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Agent Parameters State
  const [userId, setUserId] = useState('langgraph-chat-ui-user');
  const [systemPrompt, setSystemPrompt] = useState('Você é a EAI, assistente virtual da Prefeitura do Rio de Janeiro.');
  const [modelName, setModelName] = useState('gemini-1.5-flash-latest');
  const [temperature, setTemperature] = useState(0.7);
  const [historyLimit, setHistoryLimit] = useState(4);
  const [embeddingLimit, setEmbeddingLimit] = useState(2);
  const [provider, setProvider] = useState('google');


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
      const agentConfig: AgentConfig = {
        provider,
        temperature,
        model_name: modelName,
        system_prompt: systemPrompt,
        history_limit: historyLimit,
        embedding_limit: embeddingLimit,
      };

      const payload: ChatRequestPayload = {
        user_id: userId,
        prompt: input,
        agent_config: agentConfig,
      };

      const botResponseData = await sendChatMessage(payload, token);
      const assistantMessage = botResponseData.find(m => m.type === 'ai');
      
      const botMessage: DisplayMessage = { 
        sender: 'bot', 
        content: assistantMessage?.data.content || "Não foi possível obter uma resposta do assistente.",
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

  return (
    <div className="grid md:grid-cols-[1fr_350px] gap-6 h-full">
      {/* Painel do Chat (Esquerda) */}
      <Card className="flex flex-col h-full overflow-hidden">
        <CardHeader>
          <CardTitle>Chat LangGraph (RAG)</CardTitle>
        </CardHeader>
        <CardContent ref={scrollAreaRef} className="flex-1 overflow-y-auto p-4">
            <div className="space-y-4">
              {messages.map((msg, index) => (
                <div key={index} className={`flex items-start gap-3 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
                  {msg.sender === 'bot' && <Bot className="h-6 w-6 text-primary flex-shrink-0" />}
                  <div className={`w-full max-w-[80%] rounded-lg ${msg.sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                    <div 
                      className="prose prose-sm dark:prose-invert p-4 max-w-full"
                      dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked(msg.content) as string) }}
                    />
                    {msg.sender === 'bot' && msg.fullResponse && (
                      <Accordion type="single" collapsible className="w-full bg-background/50 rounded-b-lg">
                        <AccordionItem value="item-1" className="border-x-0 border-b-0">
                          <AccordionTrigger className="px-4 py-2 text-xs">Ver Contexto</AccordionTrigger>
                          <AccordionContent className="p-4 space-y-4">
                            {msg.fullResponse.filter(m => m.type === 'context').map((step, stepIndex) => (
                              <div key={stepIndex} className="space-y-2">
                                <div className="flex items-center gap-2">
                                  <BookText className="h-4 w-4 text-blue-500" />
                                  <h4 className="font-semibold">Contexto Utilizado</h4>
                                </div>
                                <JsonViewer data={step.data.content} />
                              </div>
                            ))}
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
            <Label htmlFor="user-id">User ID</Label>
            <Input
                id="user-id"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
            />
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
            <Input
              id="model"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
            />
          </div>
           <div className="space-y-2">
            <Label htmlFor="provider">Provider</Label>
            <Input
              id="provider"
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="temperature">Temperature</Label>
            <Input
              id="temperature"
              type="number"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              step="0.1"
            />
          </div>
           <div className="space-y-2">
            <Label htmlFor="history-limit">History Limit</Label>
            <Input
              id="history-limit"
              type="number"
              value={historyLimit}
              onChange={(e) => setHistoryLimit(parseInt(e.target.value, 10))}
            />
          </div>
           <div className="space-y-2">
            <Label htmlFor="embedding-limit">Embedding Limit</Label>
            <Input
              id="embedding-limit"
              type="number"
              value={embeddingLimit}
              onChange={(e) => setEmbeddingLimit(parseInt(e.target.value, 10))}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
