'use client';

import { useState } from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Plus, X } from 'lucide-react';
import { Service } from '../../types';

interface ChannelsTabProps {
  data: Partial<Service>;
  onChange: (field: keyof Service, value: unknown) => void;
  errors: Partial<Record<keyof Service, string>>;
}

export default function ChannelsTab({ data, onChange }: ChannelsTabProps) {
  const [newDigitalChannel, setNewDigitalChannel] = useState('');
  const [newPresentialChannel, setNewPresentialChannel] = useState('');

  const canaisDigitais = data.canais_digitais || [];
  const canaisPresenciais = data.canais_presenciais || [];

  const addDigitalChannel = () => {
    if (newDigitalChannel.trim()) {
      onChange('canais_digitais', [...canaisDigitais, newDigitalChannel.trim()]);
      setNewDigitalChannel('');
    }
  };

  const removeDigitalChannel = (index: number) => {
    onChange('canais_digitais', canaisDigitais.filter((_, i) => i !== index));
  };

  const addPresentialChannel = () => {
    if (newPresentialChannel.trim()) {
      onChange('canais_presenciais', [...canaisPresenciais, newPresentialChannel.trim()]);
      setNewPresentialChannel('');
    }
  };

  const removePresentialChannel = (index: number) => {
    onChange('canais_presenciais', canaisPresenciais.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-6">
      {/* Canais Digitais */}
      <div className="space-y-3">
        <Label>Canais Digitais</Label>
        <div className="flex gap-2">
          <Input
            value={newDigitalChannel}
            onChange={(e) => setNewDigitalChannel(e.target.value)}
            placeholder="Ex: Portal Online, Aplicativo, WhatsApp..."
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addDigitalChannel())}
          />
          <Button type="button" onClick={addDigitalChannel} size="icon">
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        {canaisDigitais.length > 0 && (
          <div className="space-y-2 border rounded-md p-3 bg-muted/30">
            {canaisDigitais.map((canal, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-background rounded border">
                <span className="text-sm">{canal}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeDigitalChannel(index)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Canais Presenciais */}
      <div className="space-y-3">
        <Label>Canais Presenciais</Label>
        <div className="flex gap-2">
          <Input
            value={newPresentialChannel}
            onChange={(e) => setNewPresentialChannel(e.target.value)}
            placeholder="Ex: Secretaria Municipal, CRAS, Unidade de Atendimento..."
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addPresentialChannel())}
          />
          <Button type="button" onClick={addPresentialChannel} size="icon">
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        {canaisPresenciais.length > 0 && (
          <div className="space-y-2 border rounded-md p-3 bg-muted/30">
            {canaisPresenciais.map((canal, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-background rounded border">
                <span className="text-sm">{canal}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removePresentialChannel(index)}
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
