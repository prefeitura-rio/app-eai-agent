import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Service } from '../../types';

interface BasicInfoTabProps {
  data: Partial<Service>;
  onChange: (field: keyof Service, value: unknown) => void;
  errors?: Partial<Record<keyof Service, string>>;
}

export default function BasicInfoTab({ data, onChange, errors }: BasicInfoTabProps) {
  const handleArrayInput = (field: keyof Service, value: string) => {
    const arrayValue = value.split(',').map(item => item.trim()).filter(Boolean);
    onChange(field, arrayValue);
  };

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="nome_servico">
          Nome do Servico <span className="text-destructive">*</span>
        </Label>
        <Input
          id="nome_servico"
          value={data.nome_servico || ''}
          onChange={(e) => onChange('nome_servico', e.target.value)}
          placeholder="Digite o nome do servico"
          maxLength={255}
          required
        />
        {errors?.nome_servico && (
          <p className="text-sm text-destructive">{errors.nome_servico}</p>
        )}
        <p className="text-xs text-muted-foreground">
          {data.nome_servico?.length || 0}/255 caracteres
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="tema_geral">
          Tema Geral <span className="text-destructive">*</span>
        </Label>
        <Input
          id="tema_geral"
          value={data.tema_geral || ''}
          onChange={(e) => onChange('tema_geral', e.target.value)}
          placeholder="Ex: Saude, Educacao, Transporte"
          required
        />
        {errors?.tema_geral && (
          <p className="text-sm text-destructive">{errors.tema_geral}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="orgao_gestor">
          Orgao Gestor <span className="text-destructive">*</span>
        </Label>
        <Input
          id="orgao_gestor"
          value={data.orgao_gestor?.join(', ') || ''}
          onChange={(e) => handleArrayInput('orgao_gestor', e.target.value)}
          placeholder="Digite os orgaos separados por virgula"
          required
        />
        {errors?.orgao_gestor && (
          <p className="text-sm text-destructive">{errors.orgao_gestor}</p>
        )}
        <p className="text-xs text-muted-foreground">
          Separe multiplos orgaos com virgula. Ex: SMTR, SECONSERVA
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="publico_especifico">
          Publico Especifico <span className="text-destructive">*</span>
        </Label>
        <Input
          id="publico_especifico"
          value={data.publico_especifico?.join(', ') || ''}
          onChange={(e) => handleArrayInput('publico_especifico', e.target.value)}
          placeholder="Digite os publicos separados por virgula"
          required
        />
        {errors?.publico_especifico && (
          <p className="text-sm text-destructive">{errors.publico_especifico}</p>
        )}
        <p className="text-xs text-muted-foreground">
          Ex: Cidadaos, Empresas, Servidores publicos
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="resumo">
          Resumo <span className="text-destructive">*</span>
        </Label>
        <Textarea
          id="resumo"
          value={data.resumo || ''}
          onChange={(e) => onChange('resumo', e.target.value)}
          placeholder="Escreva um resumo breve do servico"
          maxLength={350}
          rows={4}
          required
        />
        {errors?.resumo && (
          <p className="text-sm text-destructive">{errors.resumo}</p>
        )}
        <p className="text-xs text-muted-foreground">
          {data.resumo?.length || 0}/350 caracteres
        </p>
      </div>
    </div>
  );
}
