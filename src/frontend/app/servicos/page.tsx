'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { Checkbox } from '@/components/ui/checkbox';
import { Plus, Search, ChevronLeft, ChevronRight, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import AppHeader from '@/app/components/AppHeader';
import GovBrAuthModal from './components/GovBrAuthModal';
import StatusBadge from './components/StatusBadge';
import ServiceModal from './components/ServiceModal';
import { listServices } from './services/api';
import { isAuthenticated } from './services/govbr-auth';
import { Service, ServiceFilters } from './types';
import { formatDate, truncate } from './utils/formatters';

export default function ServicosPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showServiceModal, setShowServiceModal] = useState(false);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [filters, setFilters] = useState<ServiceFilters>({
    page: 1,
    per_page: 10,
    status: '',
    nome_servico: '',
    tema_geral: '',
    awaiting_approval: undefined,
    is_free: undefined,
  });
  const [totalFound, setTotalFound] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  useEffect(() => {
    if (!isAuthenticated()) {
      setShowAuthModal(true);
    } else {
      loadServices();
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated()) {
      loadServices();
    }
  }, [filters]);

  const loadServices = async () => {
    setIsLoading(true);
    try {
      const response = await listServices(filters);
      setServices(response.services);
      setTotalFound(response.found);
      setTotalPages(Math.ceil(response.found / (filters.per_page || 10)));
    } catch (error) {
      console.error('Erro ao carregar servicos:', error);

      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      toast.error(`Erro ao carregar servicos: ${errorMessage}`);

      if (error instanceof Error && error.message.includes('autenticado')) {
        setShowAuthModal(true);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleAuthSuccess = () => {
    toast.success('Autenticado com sucesso!');
    loadServices();
  };

  const handleCreateService = () => {
    setSelectedService(null);
    setShowServiceModal(true);
  };

  const handleEditService = (service: Service) => {
    setSelectedService(service);
    setShowServiceModal(true);
  };

  const handleServiceSaved = () => {
    loadServices();
  };

  const handleFilterChange = (key: keyof ServiceFilters, value: string | number | boolean | undefined) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: key !== 'page' ? 1 : (value as number),
    }));
  };

  const handlePageChange = (newPage: number) => {
    setFilters(prev => ({ ...prev, page: newPage }));
  };

  const clearFilters = () => {
    setFilters({
      page: 1,
      per_page: 10,
      status: '',
      nome_servico: '',
      tema_geral: '',
      awaiting_approval: undefined,
      is_free: undefined,
    });
  };

  return (
    <>
      <AppHeader
        title="Gerenciamento de Servicos"
        subtitle="Visualize, crie e edite os servicos disponiveis no portal"
      />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6 space-y-4 rounded-lg border bg-card p-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Nome do Servico</label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar..."
                  value={filters.nome_servico || ''}
                  onChange={(e) => handleFilterChange('nome_servico', e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Status</label>
              <Select
                value={filters.status?.toString() || 'all'}
                onValueChange={(value) => handleFilterChange('status', value === 'all' ? '' : Number(value) as 0 | 1)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  <SelectItem value="0">Rascunho</SelectItem>
                  <SelectItem value="1">Publicado</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Tema Geral</label>
              <Input
                placeholder="Filtrar por tema..."
                value={filters.tema_geral || ''}
                onChange={(e) => handleFilterChange('tema_geral', e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Itens por pagina</label>
              <Select
                value={filters.per_page?.toString() || '10'}
                onValueChange={(value) => handleFilterChange('per_page', Number(value))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="25">25</SelectItem>
                  <SelectItem value="50">50</SelectItem>
                  <SelectItem value="100">100</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex flex-wrap gap-4">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="awaiting"
                checked={filters.awaiting_approval || false}
                onCheckedChange={(checked) => handleFilterChange('awaiting_approval', checked as boolean)}
              />
              <label htmlFor="awaiting" className="text-sm font-medium">
                Aguardando Aprovacao
              </label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="free"
                checked={filters.is_free || false}
                onCheckedChange={(checked) => handleFilterChange('is_free', checked as boolean)}
              />
              <label htmlFor="free" className="text-sm font-medium">
                Servicos Gratuitos
              </label>
            </div>

            <Button variant="outline" size="sm" onClick={clearFilters}>
              Limpar Filtros
            </Button>
          </div>
        </div>

        <div className="mb-4 flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Mostrando {services.length} de {totalFound} resultado{totalFound !== 1 ? 's' : ''}
          </p>
          <Button onClick={handleCreateService}>
            <Plus className="mr-2 h-4 w-4" />
            Novo Servico
          </Button>
        </div>

        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome do Servico</TableHead>
                <TableHead>Tema Geral</TableHead>
                <TableHead>Orgao Gestor</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ult. Atualizacao</TableHead>
                <TableHead className="text-right">Acoes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-[200px]" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-[120px]" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-[150px]" /></TableCell>
                    <TableCell><Skeleton className="h-6 w-[80px]" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-[100px]" /></TableCell>
                    <TableCell><Skeleton className="h-8 w-[100px] ml-auto" /></TableCell>
                  </TableRow>
                ))
              ) : services.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <div className="flex flex-col items-center gap-2 text-muted-foreground">
                      <AlertCircle className="h-8 w-8" />
                      <p>Nenhum servico encontrado</p>
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                services.map((service) => (
                  <TableRow key={service.id}>
                    <TableCell className="font-medium">
                      {truncate(service.nome_servico, 40)}
                    </TableCell>
                    <TableCell>{service.tema_geral || '-'}</TableCell>
                    <TableCell>{truncate(service.orgao_gestor?.join(', ') || '-', 30)}</TableCell>
                    <TableCell>
                      <StatusBadge status={service.status} />
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDate(service.last_update)}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" onClick={() => handleEditService(service)}>
                        Editar
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {totalPages > 1 && (
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Pagina {filters.page} de {totalPages}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange((filters.page || 1) - 1)}
                disabled={filters.page === 1}
              >
                <ChevronLeft className="h-4 w-4" />
                Anterior
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange((filters.page || 1) + 1)}
                disabled={filters.page === totalPages}
              >
                Proxima
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>

      <GovBrAuthModal
        open={showAuthModal}
        onOpenChange={setShowAuthModal}
        onSuccess={handleAuthSuccess}
      />

      <ServiceModal
        open={showServiceModal}
        onOpenChange={setShowServiceModal}
        service={selectedService}
        onSuccess={handleServiceSaved}
      />
    </>
  );
}
