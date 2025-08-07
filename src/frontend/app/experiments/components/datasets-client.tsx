'use client';

import React, { useState, useMemo, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Search, ArrowUp, ArrowDown, RefreshCw, Trash2 } from 'lucide-react';
import { cn } from '@/app/utils/utils';
import { useHeader } from '@/app/contexts/HeaderContext';
import { useAuth } from '@/app/contexts/AuthContext';
import { DatasetInfo } from '../types';
import { deleteDataset } from '../services/api';
import { toast } from 'sonner';

interface DatasetsClientProps {
  datasets: DatasetInfo[];
}

type SortKey = keyof DatasetInfo;

export default function DatasetsClient({ datasets: initialDatasets }: DatasetsClientProps) {
  const router = useRouter();
  const { setTitle, setSubtitle } = useHeader();
  const { token } = useAuth();
  
  const [datasets, setDatasets] = useState<DatasetInfo[]>(initialDatasets);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState<{ key: SortKey | null; direction: 'ascending' | 'descending' }>({ key: 'created_at', direction: 'descending' });
  const [isDeleting, setIsDeleting] = useState<string | null>(null);

  useEffect(() => {
    setTitle('Painel de Datasets');
    setSubtitle('Selecione um dataset para ver os experimentos');
  }, [setTitle, setSubtitle]);

  useEffect(() => {
    setDatasets(initialDatasets);
  }, [initialDatasets]);

  const handleSort = (key: SortKey) => {
    let direction: 'ascending' | 'descending' = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const filteredAndSortedDatasets = useMemo(() => {
    let sortableItems = [...datasets];

    if (searchTerm) {
      sortableItems = sortableItems.filter(item =>
        item.dataset_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (sortConfig.key) {
      sortableItems.sort((a, b) => {
        const aValue = a[sortConfig.key!];
        const bValue = b[sortConfig.key!];

        if (aValue < bValue) return sortConfig.direction === 'ascending' ? -1 : 1;
        if (aValue > bValue) return sortConfig.direction === 'ascending' ? 1 : -1;
        return 0;
      });
    }

    return sortableItems;
  }, [datasets, searchTerm, sortConfig]);

  const handleRowClick = (datasetId: string) => {
    router.push(`/experiments/${datasetId}`);
  };

  const handleDeleteDataset = async (datasetId: string, datasetName: string) => {
    if (isDeleting === datasetId || !token) return;
    
    setIsDeleting(datasetId);
    
    try {
      await deleteDataset(datasetId, token);
      
      // Remove the dataset from the local state
      setDatasets(prev => prev.filter(dataset => dataset.dataset_id !== datasetId));
      
      toast.success(`Dataset "${datasetName}" deletado com sucesso!`);
    } catch (error) {
      console.error('Error deleting dataset:', error);
      toast.error(`Erro ao deletar dataset "${datasetName}": ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
    } finally {
      setIsDeleting(null);
    }
  };

  const tableHeaders: { key: keyof DatasetInfo; label: string; className?: string }[] = [
    { key: 'dataset_name', label: 'Nome', className: 'w-[25%]' },
    { key: 'dataset_description', label: 'Descrição' },
    { key: 'num_examples', label: 'Exemplos', className: 'text-center w-[100px]' },
    { key: 'num_runs', label: 'Execuções', className: 'text-center w-[100px]' },
    { key: 'created_at', label: 'Criado em', className: 'text-center w-[150px]' },
    { key: 'actions', label: 'Ações', className: 'text-center w-[100px]' },
  ];

  return (
    <div className="space-y-4">
        <div className="flex items-center justify-end gap-4">
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Filtrar por nome..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" onClick={() => window.location.reload()} size="icon">
                  <RefreshCw className="h-4 w-4 text-primary" />
                </Button>
              </TooltipTrigger>
              <TooltipContent><p>Atualizar</p></TooltipContent>
            </Tooltip>
        </div>
      <div className="overflow-auto h-[calc(100vh-16rem)] border rounded-lg">
          <Table>
            <TableHeader className="sticky top-0 bg-background">
              <TableRow>
                {tableHeaders.map(({ key, label, className }) => (
                  <TableHead key={key} className={cn("p-4", className)}>
                    <div className="flex items-center justify-center">
                      {key === 'actions' ? (
                        <span className="text-sm font-medium">{label}</span>
                      ) : (
                        <Button variant="ghost" onClick={() => handleSort(key as SortKey)} className="px-2">
                          {label}
                          {sortConfig.key === key && (
                            sortConfig.direction === 'ascending' ? <ArrowUp className="ml-2 h-4 w-4" /> : <ArrowDown className="ml-2 h-4 w-4" />
                          )}
                        </Button>
                      )}
                    </div>
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAndSortedDatasets.length > 0 ? (
                filteredAndSortedDatasets.map((dataset) => (
                  <TableRow key={dataset.dataset_id} onClick={() => handleRowClick(dataset.dataset_id)} className="cursor-pointer">
                    <TableCell className="p-4 font-medium">
                      <Link href={`/experiments/${dataset.dataset_id}`} onClick={(e) => e.stopPropagation()} className="text-primary hover:underline">
                        {dataset.dataset_name}
                      </Link>
                    </TableCell>
                    <TableCell className="p-4 text-muted-foreground">{dataset.dataset_description || '—'}</TableCell>
                    <TableCell className="p-4 text-center">
                      <Badge variant="outline" className="text-sm">{dataset.num_examples}</Badge>
                    </TableCell>
                    <TableCell className="p-4 text-center">
                      <Badge className="text-sm">{dataset.num_runs}</Badge>
                    </TableCell>
                    <TableCell className="p-4 text-center text-muted-foreground text-xs">
                        <div>{new Date(dataset.created_at.replace('Z', '')).toLocaleDateString('pt-BR')}</div>
                        <div>{new Date(dataset.created_at.replace('Z', '')).toLocaleTimeString('pt-BR')}</div>
                    </TableCell>
                    <TableCell className="p-4 text-center" onClick={(e) => e.stopPropagation()}>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                            disabled={isDeleting === dataset.dataset_id}
                          >
                            {isDeleting === dataset.dataset_id ? (
                              <RefreshCw className="h-4 w-4 animate-spin" />
                            ) : (
                              <Trash2 className="h-4 w-4" />
                            )}
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Confirmar exclusão</AlertDialogTitle>
                            <AlertDialogDescription>
                              Tem certeza que deseja deletar o dataset "{dataset.dataset_name}"? 
                              Esta ação irá deletar o dataset e todos os {dataset.num_runs} experimentos associados.
                              <br /><br />
                              <strong>Esta ação não pode ser desfeita.</strong>
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancelar</AlertDialogCancel>
                            <AlertDialogAction
                              onClick={() => handleDeleteDataset(dataset.dataset_id, dataset.dataset_name)}
                              className="bg-red-500 hover:bg-red-600"
                            >
                              Deletar Dataset
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                    <TableCell colSpan={tableHeaders.length} className="h-24 text-center">
                        Nenhum dataset encontrado.
                    </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
      </div>
    </div>
  );
}
