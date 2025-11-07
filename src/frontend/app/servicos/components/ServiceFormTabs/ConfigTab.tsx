'use client';

import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Service, ServiceAgents } from '../../types';

interface ConfigTabProps {
  data: Partial<Service>;
  onChange: (field: keyof Service, value: unknown) => void;
  errors: Partial<Record<keyof Service, string>>;
}

export default function ConfigTab({ data, onChange }: ConfigTabProps) {
  const agents = data.agents || { exclusive_for_agents: false, tool_hint: '' };
  const extraFields = data.extra_fields || {};

  const handleAgentsChange = (field: keyof ServiceAgents, value: unknown) => {
    onChange('agents', { ...agents, [field]: value });
  };

  const handleExtraFieldsChange = (jsonString: string) => {
    try {
      const parsed = JSON.parse(jsonString);
      onChange('extra_fields', parsed);
    } catch {
      // Invalid JSON, ignore
    }
  };

  const formatDate = (timestamp?: number) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp * 1000).toLocaleString('pt-BR');
  };

  return (
    <div className="space-y-6">
      {/* Metadados */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold">Metadados</h3>
        <div className="grid grid-cols-2 gap-4 p-4 bg-muted/30 rounded-md border">
          <div className="space-y-2">
            <Label htmlFor="service_id">ID</Label>
            <Input
              id="service_id"
              value={data.id || ''}
              onChange={(e) => onChange('id', e.target.value)}
              placeholder="Deixe vazio para gerar automaticamente"
            />
            <p className="text-xs text-muted-foreground">
              Opcional: defina um ID customizado ou deixe vazio para gerar automaticamente
            </p>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Autor (Somente Leitura)</Label>
            <Input value={data.autor || 'N/A'} disabled />
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Criado em</Label>
            <Input value={formatDate(data.created_at)} disabled />
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Ultima Atualizacao</Label>
            <Input value={formatDate(data.last_update)} disabled />
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Publicado em</Label>
            <Input value={formatDate(data.published_at)} disabled />
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Status do Embedding</Label>
            <Input
              value={data.embedding ? `${data.embedding.length} dimensoes` : 'Nao gerado'}
              disabled
            />
          </div>
        </div>
      </div>

      <Separator />

      {/* Configuracoes de Agentes */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold">Configuracoes de Agentes IA</h3>

        <div className="flex items-center space-x-2">
          <Switch
            checked={agents.exclusive_for_agents}
            onCheckedChange={(checked) => handleAgentsChange('exclusive_for_agents', checked)}
          />
          <Label>Exclusivo para Agentes IA</Label>
        </div>

        <div className="space-y-2">
          <Label htmlFor="tool_hint">Tool Hint (Dica para IA)</Label>
          <Textarea
            id="tool_hint"
            value={agents.tool_hint || ''}
            onChange={(e) => handleAgentsChange('tool_hint', e.target.value)}
            placeholder="Instrucoes especiais para agentes IA sobre como utilizar este servico..."
            rows={4}
          />
          <p className="text-xs text-muted-foreground">
            Forneca contexto adicional para que agentes de IA possam recomendar este servico adequadamente
          </p>
        </div>
      </div>

      <Separator />

      {/* Campos Extras JSON */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold">Campos Extras (JSON)</h3>
        <div className="space-y-2">
          <Label htmlFor="extra_fields">Extra Fields</Label>
          <Textarea
            id="extra_fields"
            value={JSON.stringify(extraFields, null, 2)}
            onChange={(e) => handleExtraFieldsChange(e.target.value)}
            placeholder='{"campo_customizado": "valor"}'
            rows={6}
            className="font-mono text-xs"
          />
          <p className="text-xs text-muted-foreground">
            Campos adicionais em formato JSON. Utilize para armazenar metadados especificos.
          </p>
        </div>
      </div>

      <Separator />

      {/* Search Content Preview */}
      {data.search_content && (
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground">Conteudo de Busca (Gerado Automaticamente)</Label>
          <Textarea
            value={data.search_content}
            disabled
            rows={4}
            className="text-xs"
          />
        </div>
      )}
    </div>
  );
}
