'use client';

import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { FlatMessage } from './dashboard';
import { formatDateTime } from '@/app/utils/date-formatter';

interface TableMessagesProps {
  flatMessages: FlatMessage[];
  showCard?: boolean;
}

export default function TableMessages({ flatMessages, showCard = true }: TableMessagesProps) {
  const [filters, setFilters] = useState<{ [key: string]: string }>({});
  
  const formatValue = (value: unknown): string => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'object') return JSON.stringify(value);
    if (typeof value === 'boolean') return value ? 'true' : 'false';
    if (typeof value === 'number') return value.toString();
    return String(value);
  };

  // Filter messages based on current filters
  const filteredMessages = useMemo(() => {
    return flatMessages.filter(message => {
      return Object.entries(filters).every(([column, filterValue]) => {
        if (!filterValue) return true; // No filter applied
        
        const messageValue = message[column as keyof FlatMessage];
        const valueString = formatValue(messageValue).toLowerCase();
        return valueString.includes(filterValue.toLowerCase());
      });
    });
  }, [flatMessages, filters]);

  const handleFilterChange = (column: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [column]: value
    }));
  };

  const tableContent = (
    <div className="overflow-auto h-full">
      <Table>
        <TableHeader className="sticky top-0 bg-background">
          <TableRow>
            <TableHead className="p-2">
              <div>user_id</div>
              <Input
                placeholder="Filtrar..."
                value={filters.user_id || ''}
                onChange={(e) => handleFilterChange('user_id', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>group_name</div>
              <Input
                placeholder="Filtrar..."
                value={filters.group_name || ''}
                onChange={(e) => handleFilterChange('group_name', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>id</div>
              <Input
                placeholder="Filtrar..."
                value={filters.id || ''}
                onChange={(e) => handleFilterChange('id', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>date</div>
              <Input
                placeholder="Filtrar..."
                value={filters.date || ''}
                onChange={(e) => handleFilterChange('date', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>session_id</div>
              <Input
                placeholder="Filtrar..."
                value={filters.session_id || ''}
                onChange={(e) => handleFilterChange('session_id', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>time_since_last_message</div>
              <Input
                placeholder="Filtrar..."
                value={filters.time_since_last_message || ''}
                onChange={(e) => handleFilterChange('time_since_last_message', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>name</div>
              <Input
                placeholder="Filtrar..."
                value={filters.name || ''}
                onChange={(e) => handleFilterChange('name', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>otid</div>
              <Input
                placeholder="Filtrar..."
                value={filters.otid || ''}
                onChange={(e) => handleFilterChange('otid', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>sender_id</div>
              <Input
                placeholder="Filtrar..."
                value={filters.sender_id || ''}
                onChange={(e) => handleFilterChange('sender_id', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>step_id</div>
              <Input
                placeholder="Filtrar..."
                value={filters.step_id || ''}
                onChange={(e) => handleFilterChange('step_id', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>is_err</div>
              <Input
                placeholder="Filtrar..."
                value={filters.is_err || ''}
                onChange={(e) => handleFilterChange('is_err', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>model_name</div>
              <Input
                placeholder="Filtrar..."
                value={filters.model_name || ''}
                onChange={(e) => handleFilterChange('model_name', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>finish_reason</div>
              <Input
                placeholder="Filtrar..."
                value={filters.finish_reason || ''}
                onChange={(e) => handleFilterChange('finish_reason', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>avg_logprobs</div>
              <Input
                placeholder="Filtrar..."
                value={filters.avg_logprobs || ''}
                onChange={(e) => handleFilterChange('avg_logprobs', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>usage_metadata</div>
              <Input
                placeholder="Filtrar..."
                value={filters.usage_metadata || ''}
                onChange={(e) => handleFilterChange('usage_metadata', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>message_type</div>
              <Input
                placeholder="Filtrar..."
                value={filters.message_type || ''}
                onChange={(e) => handleFilterChange('message_type', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>content</div>
              <Input
                placeholder="Filtrar..."
                value={filters.content || ''}
                onChange={(e) => handleFilterChange('content', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>tool_call</div>
              <Input
                placeholder="Filtrar..."
                value={filters.tool_call || ''}
                onChange={(e) => handleFilterChange('tool_call', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>tool_return</div>
              <Input
                placeholder="Filtrar..."
                value={filters.tool_return || ''}
                onChange={(e) => handleFilterChange('tool_return', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>status</div>
              <Input
                placeholder="Filtrar..."
                value={filters.status || ''}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>tool_call_id</div>
              <Input
                placeholder="Filtrar..."
                value={filters.tool_call_id || ''}
                onChange={(e) => handleFilterChange('tool_call_id', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>stdout</div>
              <Input
                placeholder="Filtrar..."
                value={filters.stdout || ''}
                onChange={(e) => handleFilterChange('stdout', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
            <TableHead className="p-2">
              <div>stderr</div>
              <Input
                placeholder="Filtrar..."
                value={filters.stderr || ''}
                onChange={(e) => handleFilterChange('stderr', e.target.value)}
                className="h-6 text-xs mt-1"
              />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredMessages.map((message, index) => (
            <TableRow key={`${message.id}-${index}`} className="hover:bg-muted/50">
              <TableCell className="font-mono text-xs max-w-[100px] truncate">
                {message.user_id.slice(-10)}
              </TableCell>
              <TableCell className="text-xs">
                <span className="px-2 py-1 rounded bg-indigo-100 text-indigo-800 text-xs">
                  {message.group_name}
                </span>
              </TableCell>
              <TableCell className="font-mono text-xs max-w-[100px] truncate">
                {formatValue(message.id)}
              </TableCell>
              <TableCell className="text-xs max-w-[140px]">
                {formatDateTime(message.date)}
              </TableCell>
              <TableCell className="font-mono text-xs max-w-[100px] truncate">
                {formatValue(message.session_id)}
              </TableCell>
              <TableCell className="text-xs">
                {formatValue(message.time_since_last_message)}
              </TableCell>
              <TableCell className="text-xs max-w-[100px] truncate">
                {formatValue(message.name)}
              </TableCell>
              <TableCell className="font-mono text-xs max-w-[100px] truncate">
                {formatValue(message.otid)}
              </TableCell>
              <TableCell className="text-xs">
                {formatValue(message.sender_id)}
              </TableCell>
              <TableCell className="font-mono text-xs max-w-[100px] truncate">
                {formatValue(message.step_id)}
              </TableCell>
              <TableCell className="text-xs">
                {message.is_err === true ? 
                  <span className="text-red-600">✗</span> : 
                  message.is_err === false ? 
                  <span className="text-green-600">✓</span> : 
                  '-'
                }
              </TableCell>
              <TableCell className="text-xs max-w-[100px] truncate">
                {formatValue(message.model_name)}
              </TableCell>
              <TableCell className="text-xs">
                {formatValue(message.finish_reason)}
              </TableCell>
              <TableCell className="text-xs">
                {message.avg_logprobs ? message.avg_logprobs.toFixed(3) : '-'}
              </TableCell>
              <TableCell className="text-xs max-w-[150px] truncate" title={formatValue(message.usage_metadata)}>
                {formatValue(message.usage_metadata)}
              </TableCell>
              <TableCell className="text-xs">
                <span className={`px-2 py-1 rounded text-xs ${
                  message.message_type === 'user_message' ? 'bg-blue-100 text-blue-800' :
                  message.message_type === 'assistant_message' ? 'bg-green-100 text-green-800' :
                  message.message_type === 'tool_call_message' ? 'bg-orange-100 text-orange-800' :
                  message.message_type === 'tool_return_message' ? 'bg-purple-100 text-purple-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {message.message_type}
                </span>
              </TableCell>
              <TableCell className="text-xs max-w-[200px] truncate" title={message.content}>
                {formatValue(message.content)}
              </TableCell>
              <TableCell className="text-xs max-w-[150px] truncate" title={formatValue(message.tool_call)}>
                {formatValue(message.tool_call)}
              </TableCell>
              <TableCell className="text-xs max-w-[150px] truncate" title={formatValue(message.tool_return)}>
                {formatValue(message.tool_return)}
              </TableCell>
              <TableCell className="text-xs">
                {formatValue(message.status)}
              </TableCell>
              <TableCell className="font-mono text-xs max-w-[100px] truncate">
                {formatValue(message.tool_call_id)}
              </TableCell>
              <TableCell className="text-xs max-w-[100px] truncate">
                {formatValue(message.stdout)}
              </TableCell>
              <TableCell className="text-xs max-w-[100px] truncate">
                {formatValue(message.stderr)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );

  if (!showCard) {
    return (
      <>
        {tableContent}
        {filteredMessages.length === 0 && (
          <div className="h-[200px] flex items-center justify-center text-muted-foreground">
            {Object.keys(filters).some(key => filters[key]) ? 
              'Nenhuma mensagem encontrada com os filtros aplicados' : 
              'Nenhuma mensagem encontrada'
            }
          </div>
        )}
      </>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tabela de Mensagens - Dados Originais</CardTitle>
        <p className="text-sm text-muted-foreground">
          Mostrando {filteredMessages.length} de {flatMessages.length} mensagens
          {Object.keys(filters).some(key => filters[key]) && ' (filtradas)'}
        </p>
      </CardHeader>
      <CardContent className="p-0">
        {tableContent}
        
        {filteredMessages.length === 0 && (
          <div className="h-[200px] flex items-center justify-center text-muted-foreground">
            {Object.keys(filters).some(key => filters[key]) ? 
              'Nenhuma mensagem encontrada com os filtros aplicados' : 
              'Nenhuma mensagem encontrada'
            }
          </div>
        )}
      </CardContent>
    </Card>
  );
}