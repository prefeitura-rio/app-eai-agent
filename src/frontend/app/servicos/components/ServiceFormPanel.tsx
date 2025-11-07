'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Save, FileText, X, Trash2, EyeOff } from 'lucide-react';
import { toast } from 'sonner';
import BasicInfoTab from './ServiceFormTabs/BasicInfoTab';
import { Service } from '../types';
import { createService, updateService, deleteService, unpublishService } from '../services/api';

interface ServiceFormPanelProps {
  service?: Service | null;
  onSuccess?: () => void;
  onClose: () => void;
}

export default function ServiceFormPanel({ service, onSuccess, onClose }: ServiceFormPanelProps) {
  const [formData, setFormData] = useState<Partial<Service>>({
    status: 0,
    is_free: false,
    awaiting_approval: false,
    fixar_destaque: false,
  });
  const [errors, setErrors] = useState<Partial<Record<keyof Service, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState('basico');

  const isEditing = !!service?.id;

  useEffect(() => {
    if (service) {
      setFormData(service);
    } else {
      setFormData({
        status: 0,
        is_free: false,
        awaiting_approval: false,
        fixar_destaque: false,
      });
    }
    setErrors({});
    setActiveTab('basico');
  }, [service]);

  const handleFieldChange = (field: keyof Service, value: unknown) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof Service, string>> = {};

    if (!formData.nome_servico?.trim()) {
      newErrors.nome_servico = 'Nome do servico e obrigatorio';
    } else if (formData.nome_servico.length > 255) {
      newErrors.nome_servico = 'Maximo de 255 caracteres';
    }

    if (!formData.tema_geral?.trim()) {
      newErrors.tema_geral = 'Tema geral e obrigatorio';
    }

    if (!formData.orgao_gestor || formData.orgao_gestor.length === 0) {
      newErrors.orgao_gestor = 'Pelo menos um orgao gestor e obrigatorio';
    }

    if (!formData.publico_especifico || formData.publico_especifico.length === 0) {
      newErrors.publico_especifico = 'Pelo menos um publico especifico e obrigatorio';
    }

    if (!formData.resumo?.trim()) {
      newErrors.resumo = 'Resumo e obrigatorio';
    } else if (formData.resumo.length > 350) {
      newErrors.resumo = 'Maximo de 350 caracteres';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (asDraft: boolean = true) => {
    if (!validateForm()) {
      toast.error('Preencha todos os campos obrigatorios');
      setActiveTab('basico');
      return;
    }

    setIsSubmitting(true);

    try {
      const dataToSubmit: Service = {
        ...formData,
        status: asDraft ? 0 : 1,
        awaiting_approval: !asDraft,
      } as Service;

      if (isEditing && service?.id) {
        await updateService(service.id, dataToSubmit);
        toast.success('Servico atualizado com sucesso!');
      } else {
        await createService(dataToSubmit);
        toast.success('Servico criado com sucesso!');
      }

      onSuccess?.();
    } catch (error) {
      console.error('Erro ao salvar servico:', error);
      toast.error(error instanceof Error ? error.message : 'Erro ao salvar servico');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!service?.id) return;

    if (!confirm('Tem certeza que deseja excluir este servico? Esta acao nao pode ser desfeita.')) {
      return;
    }

    setIsSubmitting(true);
    try {
      await deleteService(service.id);
      toast.success('Servico excluido com sucesso!');
      onSuccess?.();
    } catch (error) {
      console.error('Erro ao excluir servico:', error);
      toast.error(error instanceof Error ? error.message : 'Erro ao excluir servico');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUnpublish = async () => {
    if (!service?.id) return;

    if (!confirm('Tem certeza que deseja despublicar este servico?')) {
      return;
    }

    setIsSubmitting(true);
    try {
      console.log('Despublicando servico ID:', service.id);
      await unpublishService(service.id);
      toast.success('Servico despublicado com sucesso!');
      onSuccess?.();
    } catch (error) {
      console.error('Erro ao despublicar servico:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido ao despublicar servico';
      toast.error(errorMessage, { duration: 5000 });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 p-6">
      <div className="bg-card rounded-lg border shadow-sm">
        <div className="flex items-center justify-between p-4 border-b bg-muted/30">
          <div className="flex items-center gap-3">
            <FileText className="h-5 w-5" />
            <h2 className="text-lg font-semibold">
              {isEditing ? 'Editar Servico' : 'Novo Servico'}
            </h2>
          </div>
          <div className="flex items-center gap-2">
            {isEditing && service?.status === 1 && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleUnpublish}
                disabled={isSubmitting}
              >
                <EyeOff className="mr-2 h-4 w-4" />
                Despublicar
              </Button>
            )}
            {isEditing && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleDelete}
                disabled={isSubmitting}
                className="text-destructive hover:text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Excluir
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleSubmit(true)}
              disabled={isSubmitting}
            >
              {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              <Save className="mr-2 h-4 w-4" />
              Salvar
            </Button>
            <Button
              size="sm"
              onClick={() => handleSubmit(false)}
              disabled={isSubmitting}
            >
              {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Publicar
            </Button>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="p-4">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-6">
              <TabsTrigger value="basico">Basico</TabsTrigger>
              <TabsTrigger value="detalhes">Detalhes</TabsTrigger>
              <TabsTrigger value="canais">Canais</TabsTrigger>
              <TabsTrigger value="documentos">Documentos</TabsTrigger>
              <TabsTrigger value="botoes">Botoes</TabsTrigger>
              <TabsTrigger value="config">Config</TabsTrigger>
            </TabsList>

            <TabsContent value="basico" className="mt-4">
              <BasicInfoTab data={formData} onChange={handleFieldChange} errors={errors} />
            </TabsContent>

            <TabsContent value="detalhes" className="mt-4">
              <div className="flex items-center justify-center py-8 text-muted-foreground">
                <p>Tab Detalhes - Em desenvolvimento</p>
              </div>
            </TabsContent>

            <TabsContent value="canais" className="mt-4">
              <div className="flex items-center justify-center py-8 text-muted-foreground">
                <p>Tab Canais - Em desenvolvimento</p>
              </div>
            </TabsContent>

            <TabsContent value="documentos" className="mt-4">
              <div className="flex items-center justify-center py-8 text-muted-foreground">
                <p>Tab Documentos - Em desenvolvimento</p>
              </div>
            </TabsContent>

            <TabsContent value="botoes" className="mt-4">
              <div className="flex items-center justify-center py-8 text-muted-foreground">
                <p>Tab Botoes - Em desenvolvimento</p>
              </div>
            </TabsContent>

            <TabsContent value="config" className="mt-4">
              <div className="flex items-center justify-center py-8 text-muted-foreground">
                <p>Tab Configuracoes - Em desenvolvimento</p>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
