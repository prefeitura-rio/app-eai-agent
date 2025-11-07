'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Plus, Search, ChevronLeft, ChevronRight, AlertCircle, FileText, Filter, X } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { cn } from '@/app/utils/utils';
import AppHeader from '@/app/components/AppHeader';
import GovBrAuthModal from './components/GovBrAuthModal';
import StatusBadge from './components/StatusBadge';
import ServiceFormPanel from './components/ServiceFormPanel';
import { listServices, getFilterOptions } from './services/api';
import { isAuthenticated } from './services/govbr-auth';
import { Service, ServiceFilters, FilterOptions } from './types';
import { formatDate } from './utils/formatters';

export default function ServicosPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [isCreatingNew, setIsCreatingNew] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<ServiceFilters>({
    page: 1,
    per_page: 100,
    status: '',
    nome_servico: '',
    tema_geral: '',
    author: '',
    awaiting_approval: undefined,
    is_free: undefined,
  });
  const [totalFound, setTotalFound] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({
    tema_geral: [],
    autor: [],
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      setShowAuthModal(true);
    } else {
      loadServices();
      loadFilterOptions();
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
      setTotalPages(Math.ceil(response.found / (filters.per_page || 20)));
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

  const loadFilterOptions = async () => {
    try {
      const options = await getFilterOptions();
      setFilterOptions(options);
    } catch (error) {
      console.error('Erro ao carregar opcoes de filtro:', error);
    }
  };

  const handleAuthSuccess = () => {
    toast.success('Autenticado com sucesso!');
    loadServices();
    loadFilterOptions();
  };

  const handleCreateService = () => {
    setSelectedService(null);
    setIsCreatingNew(true);
  };

  const handleSelectService = (service: Service) => {
    setSelectedService(service);
    setIsCreatingNew(false);
  };

  const handleServiceSaved = () => {
    loadServices();
    setSelectedService(null);
    setIsCreatingNew(false);
  };

  const handleClosePanel = () => {
    setSelectedService(null);
    setIsCreatingNew(false);
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
      per_page: 100,
      status: '',
      nome_servico: '',
      tema_geral: '',
      author: '',
      awaiting_approval: undefined,
      is_free: undefined,
    });
  };

  const countActiveFilters = () => {
    let count = 0;
    if (filters.status !== '') count++;
    if (filters.tema_geral) count++;
    if (filters.author) count++;
    if (filters.awaiting_approval !== undefined) count++;
    if (filters.is_free !== undefined) count++;
    return count;
  };

  const showPanel = selectedService !== null || isCreatingNew;
  const activeFiltersCount = countActiveFilters();

  return (
    <div className="h-screen flex flex-col">
      <AppHeader
        title="Gerenciamento de Servicos"
        subtitle="Visualize, crie e edite os servicos disponiveis no portal"
      />

      <div className="flex-1 overflow-hidden">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 h-full py-6">
          <div className="grid md:grid-cols-[380px_1fr] gap-6 h-full">
          {/* Painel Esquerdo - Lista de Servicos */}
          <Card className="flex flex-col h-full overflow-hidden">
            <CardHeader className="flex-shrink-0 pb-4">
              <div className="space-y-4">
                {/* Barra de busca e botoes */}
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Buscar servicos..."
                      value={filters.nome_servico || ''}
                      onChange={(e) => handleFilterChange('nome_servico', e.target.value)}
                      className="pl-9"
                    />
                  </div>
                  <Button variant="outline" size="icon" onClick={() => setShowFilters(!showFilters)} className="relative">
                    <Filter className="h-4 w-4" />
                    {activeFiltersCount > 0 && (
                      <Badge variant="destructive" className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs">
                        {activeFiltersCount}
                      </Badge>
                    )}
                  </Button>
                  <Button onClick={handleCreateService} size="icon">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>

                {/* Filtros expandidos */}
                {showFilters && (
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-2">
                      <Select
                        value={filters.status?.toString() || 'all'}
                        onValueChange={(value) => handleFilterChange('status', value === 'all' ? '' : Number(value) as 0 | 1)}
                      >
                        <SelectTrigger className="text-xs h-9">
                          <SelectValue placeholder="Status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">Todos os status</SelectItem>
                          <SelectItem value="0">Rascunho</SelectItem>
                          <SelectItem value="1">Publicado</SelectItem>
                        </SelectContent>
                      </Select>

                      <Select
                        value={filters.tema_geral || 'all'}
                        onValueChange={(value) => handleFilterChange('tema_geral', value === 'all' ? '' : value)}
                      >
                        <SelectTrigger className="text-xs h-9">
                          <SelectValue placeholder="Tema Geral" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">Todos os temas</SelectItem>
                          {filterOptions.tema_geral.map((tema) => (
                            <SelectItem key={tema} value={tema}>{tema}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>

                      <Select
                        value={filters.author || 'all'}
                        onValueChange={(value) => handleFilterChange('author', value === 'all' ? '' : value)}
                      >
                        <SelectTrigger className="text-xs h-9">
                          <SelectValue placeholder="Autor" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">Todos os autores</SelectItem>
                          {filterOptions.autor.map((autor) => (
                            <SelectItem key={autor} value={autor}>{autor}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>

                      <Select
                        value={filters.awaiting_approval === undefined ? 'all' : filters.awaiting_approval.toString()}
                        onValueChange={(value) => handleFilterChange('awaiting_approval', value === 'all' ? undefined : value === 'true')}
                      >
                        <SelectTrigger className="text-xs h-9">
                          <SelectValue placeholder="Aguardando Aprovacao" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">Aprovacao: Todos</SelectItem>
                          <SelectItem value="true">Aprovacao: Sim</SelectItem>
                          <SelectItem value="false">Aprovacao: Nao</SelectItem>
                        </SelectContent>
                      </Select>

                      <Select
                        value={filters.is_free === undefined ? 'all' : filters.is_free.toString()}
                        onValueChange={(value) => handleFilterChange('is_free', value === 'all' ? undefined : value === 'true')}
                      >
                        <SelectTrigger className="text-xs h-9">
                          <SelectValue placeholder="Gratuito" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">Gratuito: Todos</SelectItem>
                          <SelectItem value="true">Gratuito: Sim</SelectItem>
                          <SelectItem value="false">Gratuito: Nao</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={clearFilters}
                      className="w-full"
                      disabled={activeFiltersCount === 0}
                    >
                      <X className="mr-2 h-4 w-4" />
                      Limpar Filtros {activeFiltersCount > 0 && `(${activeFiltersCount})`}
                    </Button>
                  </div>
                )}

                {/* Info de resultados */}
                <div className="text-xs text-muted-foreground">
                  {totalFound} servico{totalFound !== 1 ? 's' : ''} encontrado{totalFound !== 1 ? 's' : ''}
                </div>
              </div>
            </CardHeader>

            {/* Lista de Cards */}
            <CardContent className="flex-1 overflow-y-auto p-2 min-h-0">
              <div className="space-y-2">
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <Card key={i} className="cursor-pointer">
                      <CardHeader className="pb-3">
                        <Skeleton className="h-5 w-3/4" />
                        <Skeleton className="h-4 w-1/2 mt-2" />
                      </CardHeader>
                      <CardContent>
                        <Skeleton className="h-12 w-full" />
                      </CardContent>
                    </Card>
                  ))
                ) : services.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                    <AlertCircle className="h-12 w-12 mb-4" />
                    <p className="text-sm">Nenhum servico encontrado</p>
                  </div>
                ) : (
                  services.map((service) => (
                    <div
                      key={service.id}
                      className={cn(
                        "p-3 rounded-md cursor-pointer border transition-colors",
                        selectedService?.id === service.id
                          ? "bg-primary text-primary-foreground"
                          : "hover:bg-muted/50"
                      )}
                      onClick={() => handleSelectService(service)}
                    >
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <p className="font-semibold text-sm flex-1">
                          {service.nome_servico}
                        </p>
                        <StatusBadge status={service.status} className="flex-shrink-0" />
                      </div>
                      <p className="text-xs opacity-80 mb-1">
                        {service.tema_geral || 'Sem tema'}
                      </p>
                      <p className="text-xs opacity-70 line-clamp-2">
                        {service.resumo || 'Sem resumo'}
                      </p>
                      <div className="flex items-center gap-1 mt-2 text-xs opacity-60">
                        <FileText className="h-3 w-3" />
                        {formatDate(service.last_update)}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>

            {/* Paginacao */}
            {totalPages > 1 && (
              <div className="flex-shrink-0 p-3 border-t bg-muted/30 flex items-center justify-between">
                <span className="text-xs text-muted-foreground">
                  Pagina {filters.page} de {totalPages}
                </span>
                <div className="flex gap-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange((filters.page || 1) - 1)}
                    disabled={filters.page === 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange((filters.page || 1) + 1)}
                    disabled={filters.page === totalPages}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </Card>

          {/* Painel Direito - Formulario de Edicao ou Placeholder */}
          {showPanel ? (
            <ServiceFormPanel
              service={isCreatingNew ? null : selectedService}
              onSuccess={handleServiceSaved}
              onClose={handleClosePanel}
            />
          ) : (
            <Card className="flex flex-col h-full overflow-hidden">
              <div className="h-full flex items-center justify-center">
                <div className="text-center p-12 text-muted-foreground">
                  <FileText className="h-16 w-16 mx-auto mb-4 opacity-20" />
                  <p className="text-lg font-semibold mb-2">Nenhum servico selecionado</p>
                  <p className="text-sm">Selecione um servico da lista ao lado para editar</p>
                  <p className="text-sm">ou clique no botao + para criar um novo</p>
                </div>
              </div>
            </Card>
          )}
          </div>
        </div>
      </div>

      <GovBrAuthModal
        open={showAuthModal}
        onOpenChange={setShowAuthModal}
        onSuccess={handleAuthSuccess}
      />
    </div>
  );
}
