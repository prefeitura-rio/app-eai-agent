'use client';

import React from 'react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';

interface AgentSelectorProps {
  agentTypes: string[];
  selectedAgent: string;
  onAgentChange: (agent: string) => void;
  updateAgents: boolean;
  onUpdateAgentsChange: (checked: boolean) => void;
  disabled?: boolean;
}

export default function AgentSelector({ 
  agentTypes, 
  selectedAgent, 
  onAgentChange, 
  updateAgents,
  onUpdateAgentsChange,
  disabled 
}: AgentSelectorProps) {
  return (
    <div className="grid grid-cols-[1fr_auto] items-end gap-4">
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
      <div className="flex items-center space-x-2 pb-2">
        <Switch
          id="update-agents"
          checked={updateAgents}
          onCheckedChange={onUpdateAgentsChange}
          disabled={disabled}
        />
        <Label htmlFor="update-agents">Atualizar agentes existentes</Label>
      </div>
    </div>
  );
}
