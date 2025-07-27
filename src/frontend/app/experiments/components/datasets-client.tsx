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
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Download, ArrowUp, ArrowDown } from 'lucide-react';
import { cn } from '@/app/utils/utils';

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

  const handleSort = (key: keyof Dataset) => {
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
        item.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (sortConfig.key) {
      sortableItems.sort((a, b) => {
        const aValue = a[sortConfig.key!];
        const bValue = b[sortConfig.key!];

        if (aValue === null || aValue === undefined) return 1;
        if (bValue === null || bValue === undefined) return -1;
        
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

  const handleDownload = () => {
    exportToCsv('datasets.csv', filteredAndSortedDatasets);
  };

  const tableHeaders: { key: keyof Dataset; label: string; className?: string }[] = [
    { key: 'name', label: 'Nome', className: 'w-[30%]' },
    { key: 'description', label: 'Descrição' },
    { key: 'exampleCount', label: 'Exemplos', className: 'text-center w-[120px]' },
    { key: 'experimentCount', label: 'Experimentos', className: 'text-center w-[120px]' },
    { key: 'createdAt', label: 'Criado em', className: 'text-center w-[180px]' },
  ];

  return (
    <div className="space-y-4">
        <div className="flex items-center justify-between gap-4">
            <div className="relative w-full max-w-xs">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Filtrar por nome..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>
            <Button variant="outline" onClick={handleDownload}>
              <Download className="mr-2 h-4 w-4" />
              Download CSV
            </Button>
        </div>
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                {tableHeaders.map(({ key, label, className }) => (
                  <TableHead key={key} className={cn("p-4", className)}>
                    <Button variant="ghost" onClick={() => handleSort(key)} className="w-full justify-start px-2">
                      {label}
                      {sortConfig.key === key && (
                        sortConfig.direction === 'ascending' ? <ArrowUp className="ml-2 h-4 w-4" /> : <ArrowDown className="ml-2 h-4 w-4" />
                      )}
                    </Button>
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAndSortedDatasets.length > 0 ? (
                filteredAndSortedDatasets.map((dataset) => (
                  <TableRow key={dataset.id} onClick={() => handleRowClick(dataset.id)} className="cursor-pointer">
                    <TableCell className="p-4 font-medium">{dataset.name}</TableCell>
                    <TableCell className="p-4 text-muted-foreground">{dataset.description || '—'}</TableCell>
                    <TableCell className="p-4 text-center">
                      <Badge variant="outline" className="text-sm">{dataset.exampleCount}</Badge>
                    </TableCell>
                    <TableCell className="p-4 text-center">
                      <Badge className="text-sm">{dataset.experimentCount}</Badge>
                    </TableCell>
                    <TableCell className="p-4 text-center text-muted-foreground">{new Date(dataset.createdAt).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })}</TableCell>
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
        </CardContent>
      </Card>
    </div>
  );
}