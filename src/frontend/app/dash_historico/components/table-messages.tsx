'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FlatMessage } from './dashboard';

interface TableMessagesProps {
  flatMessages: FlatMessage[];
}

export default function TableMessages({ flatMessages }: TableMessagesProps) {
  
  // DEBUG: Log dates received in table-messages
  
  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'object') return JSON.stringify(value);
    if (typeof value === 'boolean') return value ? 'true' : 'false';
    if (typeof value === 'number') return value.toString();
    return String(value);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tabela de Mensagens - Dados Originais</CardTitle>
        <p className="text-sm text-muted-foreground">
          Total de mensagens: {flatMessages.length}
        </p>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto max-h-[600px]">
          <Table>
            <TableHeader className="sticky top-0 bg-background">
              <TableRow>
                <TableHead>user_id</TableHead>
                <TableHead>group_name</TableHead>
                <TableHead>id</TableHead>
                <TableHead>date</TableHead>
                <TableHead>session_id</TableHead>
                <TableHead>time_since_last_message</TableHead>
                <TableHead>name</TableHead>
                <TableHead>otid</TableHead>
                <TableHead>sender_id</TableHead>
                <TableHead>step_id</TableHead>
                <TableHead>is_err</TableHead>
                <TableHead>model_name</TableHead>
                <TableHead>finish_reason</TableHead>
                <TableHead>avg_logprobs</TableHead>
                <TableHead>usage_metadata</TableHead>
                <TableHead>message_type</TableHead>
                <TableHead>content</TableHead>
                <TableHead>tool_call</TableHead>
                <TableHead>tool_return</TableHead>
                <TableHead>status</TableHead>
                <TableHead>tool_call_id</TableHead>
                <TableHead>stdout</TableHead>
                <TableHead>stderr</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {flatMessages.map((message, index) => (
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
                    {message.date ? new Date(message.date).toLocaleString('pt-BR') : '-'}
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
        
        {flatMessages.length === 0 && (
          <div className="h-[200px] flex items-center justify-center text-muted-foreground">
            Nenhuma mensagem encontrada
          </div>
        )}
      </CardContent>
    </Card>
  );
}