'use client';

import React, { useState, useMemo, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Dataset } from '@/app/components/types';
import { exportToCsv } from '@/app/utils/csv';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Download, ArrowUp, ArrowDown, ChevronsUpDown } from 'lucide-react';

interface DatasetsClientProps {
  datasets: Dataset[];
}

export default function DatasetsClient({ datasets: initialDatasets }: DatasetsClientProps) {
  const router = useRouter();
  const [datasets, setDatasets] = useState<Dataset[]>(initialDatasets);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState<{ key: keyof Dataset | null; direction: 'ascending' | 'descending' }>({ key: 'createdAt', direction: 'descending' });

  useEffect(() => {
    setDatasets(initialDatasets);
  }, [initialDatasets]);

  const filteredAndSortedDatasets = useMemo(() => {
    let sortableItems = [...datasets];

    if (searchTerm) {
      sortableItems = sortableItems.filter(item =>
        item.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (sortConfig.key) {
      sortableItems.sort((a, b) => {
        const aValue = a[sortConfig.key!];
        const bValue = b[sortConfig.key!];

        if (aValue === null) return 1;
        if (bValue === null) return -1;
        if (aValue < bValue) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
    }

    return sortableItems;
  }, [datasets, searchTerm, sortConfig]);

  const setSort = (key: keyof Dataset, direction: 'ascending' | 'descending') => {
    setSortConfig({ key, direction });
  };

  const handleRowClick = (datasetId: string) => {
    router.push(`/experiments/${datasetId}`);
  };

  const getSortIndicator = (key: keyof Dataset) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'ascending' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />;
  };

  const handleDownload = () => {
    exportToCsv('datasets.csv', filteredAndSortedDatasets);
  };

  const tableHeaders: { key: keyof Dataset; label: string; className?: string }[] = [
    { key: 'name', label: 'Nome' },
    { key: 'description', label: 'Descrição' },
    { key: 'exampleCount', label: 'Exemplos', className: 'text-center' },
    { key: 'experimentCount', label: 'Experimentos', className: 'text-center' },
    { key: 'createdAt', label: 'Criado em', className: 'text-center' },
  ];

  return (
    <div className="container mx-auto py-4">
      <Card>
        <CardHeader className="flex-row items-center justify-between">
          <div>
            <CardTitle>Datasets Disponíveis</CardTitle>
            <CardDescription>
              Encontrados {filteredAndSortedDatasets.length} datasets.
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Filtrar por nome..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>
            <Button variant="outline" size="icon" title="Download CSV" onClick={handleDownload}>
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                {tableHeaders.map(({ key, label, className }) => (
                  <TableHead key={key} className={className}>
                    <div className="flex items-center gap-1">
                      {label}
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-7 w-7">
                            <ChevronsUpDown className="h-3 w-3" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                          <DropdownMenuItem onClick={() => setSort(key, 'ascending')}>
                            <ArrowUp className="mr-2 h-3 w-3" /> Ascendente
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => setSort(key, 'descending')}>
                            <ArrowDown className="mr-2 h-3 w-3" /> Descendente
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                      <span className="text-xs">{getSortIndicator(key)}</span>
                    </div>
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAndSortedDatasets.map((dataset) => (
                <TableRow key={dataset.id} onClick={() => handleRowClick(dataset.id)} className="cursor-pointer">
                  <TableCell className="font-medium">{dataset.name}</TableCell>
                  <TableCell>{dataset.description || 'Sem descrição'}</TableCell>
                  <TableCell className="text-center">
                    <Badge variant="secondary">{dataset.exampleCount}</Badge>
                  </TableCell>
                  <TableCell className="text-center">
                    <Badge variant="default">{dataset.experimentCount}</Badge>
                  </TableCell>
                  <TableCell className="text-center">{new Date(dataset.createdAt).toLocaleString('pt-BR')}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}