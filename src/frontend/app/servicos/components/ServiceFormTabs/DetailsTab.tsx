'use client';

import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Service } from '../../types';

interface DetailsTabProps {
  data: Partial<Service>;
  onChange: (field: keyof Service, value: unknown) => void;
  errors: Partial<Record<keyof Service, string>>;
}

export default function DetailsTab({ data, onChange, errors }: DetailsTabProps) {
  return (
    <div className="space-y-6">
      {/* Descricao Completa */}
      <div className="space-y-2">
        <Label htmlFor="descricao_completa">Descricao Completa</Label>
        <Textarea
          id="descricao_completa"
          value={data.descricao_completa || ''}
          onChange={(e) => onChange('descricao_completa', e.target.value)}
          placeholder="Descreva detalhadamente o servico..."
          rows={6}
          className={errors.descricao_completa ? 'border-destructive' : ''}
        />
        {errors.descricao_completa && (
          <p className="text-xs text-destructive">{errors.descricao_completa}</p>
        )}
      </div>

      {/* Resultado da Solicitacao */}
      <div className="space-y-2">
        <Label htmlFor="resultado_solicitacao">Resultado da Solicitacao</Label>
        <Textarea
          id="resultado_solicitacao"
          value={data.resultado_solicitacao || ''}
          onChange={(e) => onChange('resultado_solicitacao', e.target.value)}
          placeholder="Ex: Certidao, Autorizacao, Cadastro realizado..."
          rows={3}
        />
      </div>

      {/* Instrucoes ao Solicitante */}
      <div className="space-y-2">
        <Label htmlFor="instrucoes_solicitante">Instrucoes ao Solicitante</Label>
        <Textarea
          id="instrucoes_solicitante"
          value={data.instrucoes_solicitante || ''}
          onChange={(e) => onChange('instrucoes_solicitante', e.target.value)}
          placeholder="Instrucoes e orientacoes para o cidadao..."
          rows={4}
        />
      </div>

      {/* Servico Nao Cobre */}
      <div className="space-y-2">
        <Label htmlFor="servico_nao_cobre">O que o Servico NAO Cobre</Label>
        <Textarea
          id="servico_nao_cobre"
          value={data.servico_nao_cobre || ''}
          onChange={(e) => onChange('servico_nao_cobre', e.target.value)}
          placeholder="Situacoes e casos nao cobertos por este servico..."
          rows={3}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Custo do Servico */}
        <div className="space-y-2">
          <Label htmlFor="custo_servico">Custo do Servico</Label>
          <Input
            id="custo_servico"
            value={data.custo_servico || ''}
            onChange={(e) => onChange('custo_servico', e.target.value)}
            placeholder="Ex: R$ 50,00 ou Gratuito"
          />
        </div>

        {/* Tempo de Atendimento */}
        <div className="space-y-2">
          <Label htmlFor="tempo_atendimento">Tempo de Atendimento</Label>
          <Input
            id="tempo_atendimento"
            value={data.tempo_atendimento || ''}
            onChange={(e) => onChange('tempo_atendimento', e.target.value)}
            placeholder="Ex: Ate 30 dias, Imediato..."
          />
        </div>
      </div>
    </div>
  );
}
