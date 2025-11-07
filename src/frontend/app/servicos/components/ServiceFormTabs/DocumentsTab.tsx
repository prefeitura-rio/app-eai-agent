'use client';

import { useState } from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Plus, X } from 'lucide-react';
import { Service } from '../../types';

interface DocumentsTabProps {
  data: Partial<Service>;
  onChange: (field: keyof Service, value: unknown) => void;
  errors: Partial<Record<keyof Service, string>>;
}

export default function DocumentsTab({ data, onChange }: DocumentsTabProps) {
  const [newDocument, setNewDocument] = useState('');
  const [newLegislation, setNewLegislation] = useState('');

  const documentos = data.documentos_necessarios || [];
  const legislacao = data.legislacao_relacionada || [];

  const addDocument = () => {
    if (newDocument.trim()) {
      onChange('documentos_necessarios', [...documentos, newDocument.trim()]);
      setNewDocument('');
    }
  };

  const removeDocument = (index: number) => {
    onChange('documentos_necessarios', documentos.filter((_, i) => i !== index));
  };

  const addLegislation = () => {
    if (newLegislation.trim()) {
      onChange('legislacao_relacionada', [...legislacao, newLegislation.trim()]);
      setNewLegislation('');
    }
  };

  const removeLegislation = (index: number) => {
    onChange('legislacao_relacionada', legislacao.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-6">
      {/* Documentos Necessarios */}
      <div className="space-y-3">
        <Label>Documentos Necessarios</Label>
        <div className="flex gap-2">
          <Input
            value={newDocument}
            onChange={(e) => setNewDocument(e.target.value)}
            placeholder="Ex: RG, CPF, Comprovante de Residencia..."
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addDocument())}
          />
          <Button type="button" onClick={addDocument} size="icon">
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        {documentos.length > 0 && (
          <div className="space-y-2 border rounded-md p-3 bg-muted/30">
            {documentos.map((doc, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-background rounded border">
                <span className="text-sm">{doc}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeDocument(index)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Legislacao Relacionada */}
      <div className="space-y-3">
        <Label>Legislacao Relacionada</Label>
        <div className="flex gap-2">
          <Input
            value={newLegislation}
            onChange={(e) => setNewLegislation(e.target.value)}
            placeholder="Ex: Lei Municipal 1234/2020, Decreto 5678/2021..."
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addLegislation())}
          />
          <Button type="button" onClick={addLegislation} size="icon">
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        {legislacao.length > 0 && (
          <div className="space-y-2 border rounded-md p-3 bg-muted/30">
            {legislacao.map((lei, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-background rounded border">
                <span className="text-sm">{lei}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeLegislation(index)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
