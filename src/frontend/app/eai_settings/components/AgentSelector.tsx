'use client';

import React from 'react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface AgentSelectorProps {
  agentTypes: string[];
  selectedAgent: string;
  onAgentChange: (agent: string) => void;
  disabled?: boolean;
}

export default function AgentSelector({ 
  agentTypes, 
  selectedAgent, 
  onAgentChange, 
  disabled 
}: AgentSelectorProps) {
  return (
    <div className="grid grid-cols-1 items-end gap-4">
      <div className="space-y-2">
        <Label htmlFor="agent-type">Tipo de Agente</Label>
        <Select value={selectedAgent} onValueChange={onAgentChange} disabled={disabled}>
          <SelectTrigger id="agent-type">
            <SelectValue placeholder="Selecione um tipo de agente..." />
          </SelectTrigger>
          <SelectContent>
            {agentTypes.map(type => (
              <SelectItem key={type} value={type}>
                {type}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
