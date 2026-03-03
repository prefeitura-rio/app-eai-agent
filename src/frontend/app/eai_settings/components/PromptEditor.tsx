'use client';

import React, { useState } from 'react';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { Copy, Check } from 'lucide-react';

interface PromptEditorProps {
  promptContent: string;
  onPromptChange: (content: string) => void;
  promptTokens?: number | null;
  promptTokenizer?: string | null;
  showTokenizer?: boolean;
  disabled?: boolean;
}

export default function PromptEditor({
  promptContent,
  onPromptChange,
  promptTokens,
  promptTokenizer,
  showTokenizer = false,
  disabled,
}: PromptEditorProps) {
  const [hasCopied, setHasCopied] = useState(false);
  const charCount = promptContent.length;

  const handleCopy = () => {
    navigator.clipboard.writeText(promptContent);
    setHasCopied(true);
    setTimeout(() => {
      setHasCopied(false);
    }, 2000);
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <Label htmlFor="prompt-editor">Conteúdo do Prompt</Label>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="ghost" size="icon" onClick={handleCopy} disabled={disabled}>
              {hasCopied ? <Check className="h-4 w-4 text-success" /> : <Copy className="h-4 w-4" />}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Copiar</p>
          </TooltipContent>
        </Tooltip>
      </div>
      <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        <span className="rounded-md border border-border bg-muted px-2 py-1">
          Tokens: {typeof promptTokens === 'number' ? promptTokens.toLocaleString('pt-BR') : '-'}
        </span>
        <span className="rounded-md border border-border bg-muted px-2 py-1">
          Caracteres: {charCount.toLocaleString('pt-BR')}
        </span>
        {showTokenizer && promptTokenizer && (
          <span className="rounded-md border border-border bg-muted px-2 py-1">
            {promptTokenizer}
          </span>
        )}
      </div>
      <Textarea
        id="prompt-editor"
        value={promptContent}
        onChange={(e) => onPromptChange(e.target.value)}
        disabled={disabled}
        className="h-[400px] resize-y font-mono text-xs"
        placeholder="Digite o prompt do sistema aqui..."
      />
    </div>
  );
}
