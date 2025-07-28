'use client';

import React from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';

interface AgentConfigurationProps {
  memoryBlocks: string;
  onMemoryBlocksChange: (value: string) => void;
  tools: string;
  onToolsChange: (value: string) => void;
  modelName: string;
  onModelNameChange: (value: string) => void;
  embeddingName: string;
  onEmbeddingNameChange: (value: string) => void;
  updateAgents: boolean;
  onUpdateAgentsChange: (value: boolean) => void;
  disabled?: boolean;
}

export default function AgentConfiguration({
  memoryBlocks, onMemoryBlocksChange,
  tools, onToolsChange,
  modelName, onModelNameChange,
  embeddingName, onEmbeddingNameChange,
  disabled
}: AgentConfigurationProps) {
  return (
    <div className="space-y-6">

      <div className="grid md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="tools">Tools (separado por vírgula)</Label>
          <Input
            id="tools"
            value={tools}
            onChange={(e) => onToolsChange(e.target.value)}
            disabled={disabled}
            placeholder="ferramenta_1,ferramenta_2"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="model-name">Model</Label>
          <Input
            id="model-name"
            value={modelName}
            onChange={(e) => onModelNameChange(e.target.value)}
            disabled={disabled}
            placeholder="gemini-1.5-pro-latest"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="embedding-name">Embedding</Label>
          <Input
            id="embedding-name"
            value={embeddingName}
            onChange={(e) => onEmbeddingNameChange(e.target.value)}
            disabled={disabled}
            placeholder="text-embedding-004"
          />
        </div>
      </div>
            <div className="space-y-2">
        <Label htmlFor="memory-blocks">Memory Blocks (JSON)</Label>
        <Textarea
          id="memory-blocks"
          value={memoryBlocks}
          onChange={(e) => onMemoryBlocksChange(e.target.value)}
          disabled={disabled}
          className="h-[240px] resize-y font-mono text-xs"
          placeholder='[{"type": "buffer_window", "config": {"k": 5}}]'
        />
      </div>
    </div>
  );
}
