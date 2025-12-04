'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Loader2, Save, FileText, X, Trash2, EyeOff } from 'lucide-react';
import { toast } from 'sonner';
import BasicInfoTab from './ServiceFormTabs/BasicInfoTab';
import DetailsTab from './ServiceFormTabs/DetailsTab';
import ChannelsTab from './ServiceFormTabs/ChannelsTab';
import DocumentsTab from './ServiceFormTabs/DocumentsTab';
import ButtonsTab from './ServiceFormTabs/ButtonsTab';
import ConfigTab from './ServiceFormTabs/ConfigTab';
import { Service } from '../types';
import { createService, updateService, deleteService, unpublishService, AuthenticationError } from '../services/api';

interface ServiceFormPanelProps {
  service?: Service | null;
  onSuccess?: () => void;
  onClose: () => void;
  onAuthError?: () => void;
}

export default function ServiceFormPanel({ service, onSuccess, onClose, onAuthError }: ServiceFormPanelProps) {
  const [formData, setFormData] = useState<Partial<Service>>({
    status: 0,
    is_free: false,
    awaiting_approval: false,
    fixar_destaque: false,
  });
  const [errors, setErrors] = useState<Partial<Record<keyof Service, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

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

      // Se for erro de autenticacao, notificar componente pai
      if (error instanceof AuthenticationError) {
        toast.error(error.message);
        onAuthError?.();
        return;
      }

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

      // Se for erro de autenticacao, notificar componente pai
      if (error instanceof AuthenticationError) {
        toast.error(error.message);
        onAuthError?.();
        return;
      }

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

      // Se for erro de autenticacao, notificar componente pai
      if (error instanceof AuthenticationError) {
        toast.error(error.message);
        onAuthError?.();
        return;
      }

      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido ao despublicar servico';
      toast.error(errorMessage, { duration: 5000 });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="flex flex-col h-full overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b bg-muted/30 flex-shrink-0">
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

      <div className="flex-1 overflow-y-auto p-4 min-h-0">
        <Accordion type="multiple" defaultValue={["basico", "config"]} className="w-full">
          <AccordionItem value="basico">
            <AccordionTrigger className="text-base font-semibold">
              Informacoes Basicas
            </AccordionTrigger>
            <AccordionContent className="pt-4">
              <p className="text-sm text-muted-foreground mb-4">
                Campos essenciais para identificacao e categorizacao do servico
              </p>
              <BasicInfoTab data={formData} onChange={handleFieldChange} errors={errors} />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="config">
            <AccordionTrigger className="text-base font-semibold">
              Configuracoes Avancadas
            </AccordionTrigger>
            <AccordionContent className="pt-4">
              <p className="text-sm text-muted-foreground mb-4">
                Metadados, configuracoes de IA e campos personalizados
              </p>
              <ConfigTab data={formData} onChange={handleFieldChange} errors={errors} />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="detalhes">
            <AccordionTrigger className="text-base font-semibold">
              Detalhes do Servico
            </AccordionTrigger>
            <AccordionContent className="pt-4">
              <p className="text-sm text-muted-foreground mb-4">
                Descricao completa, resultados esperados, instrucoes e custos
              </p>
              <DetailsTab data={formData} onChange={handleFieldChange} errors={errors} />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="canais">
            <AccordionTrigger className="text-base font-semibold">
              Canais de Atendimento
            </AccordionTrigger>
            <AccordionContent className="pt-4">
              <p className="text-sm text-muted-foreground mb-4">
                Defina os canais digitais e presenciais para acesso ao servico
              </p>
              <ChannelsTab data={formData} onChange={handleFieldChange} errors={errors} />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="documentos">
            <AccordionTrigger className="text-base font-semibold">
              Documentos e Legislacao
            </AccordionTrigger>
            <AccordionContent className="pt-4">
              <p className="text-sm text-muted-foreground mb-4">
                Documentos necessarios e legislacao aplicavel ao servico
              </p>
              <DocumentsTab data={formData} onChange={handleFieldChange} errors={errors} />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="botoes">
            <AccordionTrigger className="text-base font-semibold">
              Botoes de Acao
            </AccordionTrigger>
            <AccordionContent className="pt-4">
              <p className="text-sm text-muted-foreground mb-4">
                Configure botoes que serao exibidos na pagina do servico
              </p>
              <ButtonsTab data={formData} onChange={handleFieldChange} errors={errors} />
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
    </Card>
  );
}
