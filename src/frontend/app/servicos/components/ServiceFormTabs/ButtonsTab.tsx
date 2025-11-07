'use client';

import { useState } from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, X } from 'lucide-react';
import { Service, ServiceButton } from '../../types';

interface ButtonsTabProps {
  data: Partial<Service>;
  onChange: (field: keyof Service, value: unknown) => void;
  errors: Partial<Record<keyof Service, string>>;
}

export default function ButtonsTab({ data, onChange }: ButtonsTabProps) {
  const [showForm, setShowForm] = useState(false);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [formData, setFormData] = useState<ServiceButton>({
    titulo: '',
    descricao: '',
    url_service: '',
    ordem: 0,
    is_enabled: true,
  });

  const buttons = data.buttons || [];

  const resetForm = () => {
    setFormData({
      titulo: '',
      descricao: '',
      url_service: '',
      ordem: buttons.length,
      is_enabled: true,
    });
    setEditingIndex(null);
    setShowForm(false);
  };

  const handleSubmit = () => {
    if (!formData.titulo.trim() || !formData.url_service.trim()) {
      return;
    }

    if (editingIndex !== null) {
      const updated = [...buttons];
      updated[editingIndex] = formData;
      onChange('buttons', updated);
    } else {
      onChange('buttons', [...buttons, formData]);
    }

    resetForm();
  };

  const handleEdit = (index: number) => {
    setFormData(buttons[index]);
    setEditingIndex(index);
    setShowForm(true);
  };

  const handleRemove = (index: number) => {
    onChange('buttons', buttons.filter((_, i) => i !== index));
  };

  const moveButton = (index: number, direction: 'up' | 'down') => {
    const newButtons = [...buttons];
    const newIndex = direction === 'up' ? index - 1 : index + 1;

    if (newIndex < 0 || newIndex >= newButtons.length) return;

    [newButtons[index], newButtons[newIndex]] = [newButtons[newIndex], newButtons[index]];

    // Update ordem
    newButtons.forEach((btn, idx) => {
      btn.ordem = idx;
    });

    onChange('buttons', newButtons);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Botoes de Acao ({buttons.length})</h3>
        {!showForm && (
          <Button type="button" onClick={() => setShowForm(true)} size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Adicionar Botao
          </Button>
        )}
      </div>

      {/* Form para adicionar/editar */}
      {showForm && (
        <Card className="border-primary">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">
              {editingIndex !== null ? 'Editar Botao' : 'Novo Botao'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Titulo *</Label>
                <Input
                  value={formData.titulo}
                  onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
                  placeholder="Ex: Solicitar Online"
                />
              </div>

              <div className="space-y-2">
                <Label>URL *</Label>
                <Input
                  value={formData.url_service}
                  onChange={(e) => setFormData({ ...formData, url_service: e.target.value })}
                  placeholder="https://..."
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Descricao</Label>
              <Textarea
                value={formData.descricao}
                onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                placeholder="Descricao do botao..."
                rows={2}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Ordem</Label>
                <Input
                  type="number"
                  value={formData.ordem}
                  onChange={(e) => setFormData({ ...formData, ordem: Number(e.target.value) })}
                />
              </div>

              <div className="flex items-center space-x-2 pt-6">
                <Switch
                  checked={formData.is_enabled}
                  onCheckedChange={(checked) => setFormData({ ...formData, is_enabled: checked })}
                />
                <Label>Habilitado</Label>
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              <Button type="button" onClick={handleSubmit} size="sm">
                {editingIndex !== null ? 'Atualizar' : 'Adicionar'}
              </Button>
              <Button type="button" onClick={resetForm} variant="outline" size="sm">
                Cancelar
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Lista de botões */}
      {buttons.length > 0 && (
        <div className="space-y-2">
          {buttons.map((button, index) => (
            <Card key={index} className={!button.is_enabled ? 'opacity-50' : ''}>
              <CardContent className="p-3">
                <div className="flex items-start gap-3">
                  <div className="flex flex-col gap-1 pt-1">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => moveButton(index, 'up')}
                      disabled={index === 0}
                      className="h-6 w-6 p-0"
                    >
                      ↑
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => moveButton(index, 'down')}
                      disabled={index === buttons.length - 1}
                      className="h-6 w-6 p-0"
                    >
                      ↓
                    </Button>
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-sm truncate">{button.titulo}</p>
                        <p className="text-xs text-muted-foreground truncate">{button.url_service}</p>
                        {button.descricao && (
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{button.descricao}</p>
                        )}
                        <div className="flex items-center gap-3 mt-1">
                          <span className="text-xs text-muted-foreground">Ordem: {button.ordem}</span>
                          <span className={`text-xs ${button.is_enabled ? 'text-green-600' : 'text-muted-foreground'}`}>
                            {button.is_enabled ? 'Habilitado' : 'Desabilitado'}
                          </span>
                        </div>
                      </div>

                      <div className="flex gap-1 flex-shrink-0">
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(index)}
                        >
                          Editar
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemove(index)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {buttons.length === 0 && !showForm && (
        <div className="text-center py-8 text-muted-foreground border rounded-md border-dashed">
          <p className="text-sm">Nenhum botao adicionado</p>
        </div>
      )}
    </div>
  );
}
