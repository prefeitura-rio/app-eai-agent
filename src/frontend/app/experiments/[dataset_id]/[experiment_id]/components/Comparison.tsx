'use client';

import React, { useState, useMemo } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { CardContent } from "@/components/ui/card";
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Copy, Check, Code, Eye } from 'lucide-react';

interface ComparisonProps {
  content: string;
}

export default function Comparison({ content }: ComparisonProps) {
    const [isMarkdownRendered, setIsMarkdownRendered] = useState(true);
    const [isCopied, setIsCopied] = useState(false);

    const contentHtml = useMemo(() => {
        const text = content || "";
        if (text) {
            marked.use({ breaks: true });
            return DOMPurify.sanitize(marked.parse(text) as string);
        }
        return "<p class='text-muted-foreground italic'>Nenhuma resposta disponível.</p>";
    }, [content]);

    const handleCopy = () => {
        if (!content) return;
        navigator.clipboard.writeText(content).then(() => {
            setIsCopied(true);
            setTimeout(() => setIsCopied(false), 2000);
        });
    };

    const hasContent = content && content.trim() !== '';

    return (
        <div className="relative flex-grow">
            {/* Adicionado padding-bottom para criar um espaço e evitar que o texto sobreponha os botões */}
            <CardContent className="pb-8"> 
                {isMarkdownRendered ? (
                    <div
                        className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap"
                        dangerouslySetInnerHTML={{ __html: contentHtml }}
                    />
                ) : (
                    <pre className="whitespace-pre-wrap text-sm font-mono bg-muted/50 p-4 rounded-md overflow-x-auto">
                        <code>{content || "Nenhuma resposta disponível."}</code>
                    </pre>
                )}
            </CardContent>

            {hasContent && (
                <TooltipProvider delayDuration={300}>
                    {/* 
                      AJUSTES FINAIS:
                      1. Posição: 'bottom-1 right-1' para ficar bem próximo do canto.
                      2. Sem Fundo: Removido background e blur para um visual limpo, como na imagem.
                      3. Gap: Reduzido para 'gap-0.5' para agrupar os botões.
                    */}
                    <div className="absolute bottom-0 right-6 z-10 flex items-center gap-5">
                        <Tooltip>
                            <TooltipTrigger asChild>
                                {/* 
                                  AJUSTES FINAIS:
                                  1. Tamanho do Botão: Reduzido para 'h-6 w-6', bem menor.
                                  2. Tamanho do Ícone: Reduzido para 'h-3 w-3' para manter proporção.
                                */}
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => setIsMarkdownRendered(prev => !prev)}
                                    className="h-3 w-3"
                                >
                                    {isMarkdownRendered ? <Code className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                                    <span className="sr-only">{isMarkdownRendered ? "Ver texto original" : "Renderizar Markdown"}</span>
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>{isMarkdownRendered ? "Ver texto original" : "Renderizar Markdown"}</p>
                            </TooltipContent>
                        </Tooltip>
                        
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={handleCopy}
                                    className="h-3 w-3"
                                >
                                    {isCopied ? <Check className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3 w-3" />}
                                    <span className="sr-only">Copiar texto</span>
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>{isCopied ? "Copiado!" : "Copiar texto"}</p>
                            </TooltipContent>
                        </Tooltip>
                    </div>
                </TooltipProvider>
            )}
        </div>
    );
}