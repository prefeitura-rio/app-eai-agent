'use client';

import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FlatMessage } from './dashboard';
import { formatDate, extractDateKey } from '@/app/utils/date-formatter';

interface TableMetricUserMessagesProps {
  flatMessages: FlatMessage[];
}

interface UserMessageMetrics {
  group_name: string;
  date: string;
  total_mensagens: number;
  total_sessoes: number;
  mensagens_por_sessao: number;
}

export default function TableMetricUserMessages({ flatMessages }: TableMetricUserMessagesProps) {

  // Calculate metrics grouped by group_name and date for user_messages only
  const userMessageMetrics = useMemo(() => {
    const metricsMap = new Map<string, UserMessageMetrics>();
    
    // Filter only user_messages and process them
    const userMessages = flatMessages.filter(msg => msg.message_type === 'user_message');
    
    userMessages.forEach(msg => {
      if (msg.date) {
        const dateKey = extractDateKey(msg.date);
        

        
        const key = `${msg.group_name}-${dateKey}`;
        
        if (!metricsMap.has(key)) {
          metricsMap.set(key, {
            group_name: msg.group_name,
            date: dateKey,
            total_mensagens: 0,
            total_sessoes: 0,
            mensagens_por_sessao: 0
          });
        }
        
        const metric = metricsMap.get(key)!;
        metric.total_mensagens += 1;
      }
    });
    
    // Calculate total sessions for each group/date combination from all messages
    const sessionsByGroupAndDate = new Map<string, Set<string>>();
    
    flatMessages.forEach(msg => {
      if (msg.date && msg.session_id) {
        const dateKey = extractDateKey(msg.date);
        
        const key = `${msg.group_name}-${dateKey}`;
        
        if (!sessionsByGroupAndDate.has(key)) {
          sessionsByGroupAndDate.set(key, new Set());
        }
        
        sessionsByGroupAndDate.get(key)!.add(msg.session_id);
      }
    });
    
    // Update metrics with session counts
    sessionsByGroupAndDate.forEach((sessions, key) => {
      const metric = metricsMap.get(key);
      
      if (metric) {
        metric.total_sessoes = sessions.size;
        metric.mensagens_por_sessao = metric.total_sessoes > 0 ? 
          metric.total_mensagens / metric.total_sessoes : 0;
      }
    });
    
    // Convert to array and sort by date (newest first) then by group
    const result = Array.from(metricsMap.values()).sort((a, b) => {
      const dateCompare = new Date(b.date).getTime() - new Date(a.date).getTime();
      if (dateCompare !== 0) return dateCompare;
      return a.group_name.localeCompare(b.group_name);
    });
    
    // DEBUG: Log final metrics result
    
    return result;
  }, [flatMessages]);


  return (
    <Card>
      <CardHeader>
        <CardTitle>Métricas de Mensagens de Usuários por Grupo e Data</CardTitle>
        <p className="text-sm text-muted-foreground">
          Análise diária de user_messages agrupadas por grupo. Total de registros: {userMessageMetrics.length}
        </p>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto max-h-[600px]">
          <Table>
            <TableHeader className="sticky top-0 bg-background">
              <TableRow>
                <TableHead>Group Name</TableHead>
                <TableHead>Date</TableHead>
                <TableHead className="text-right">Total Mensagens</TableHead>
                <TableHead className="text-right">Total Sessões</TableHead>
                <TableHead className="text-right">Mensagens/Sessão</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {userMessageMetrics.map((metric, index) => (
                <TableRow key={`${metric.group_name}-${metric.date}-${index}`} className="hover:bg-muted/50">
                  <TableCell>
                    <span className="px-2 py-1 rounded bg-indigo-100 text-indigo-800 text-sm font-medium">
                      {metric.group_name}
                    </span>
                  </TableCell>
                  <TableCell className="font-mono">
                    {formatDate(metric.date)}
                  </TableCell>
                  <TableCell className="text-right font-semibold">
                    {metric.total_mensagens}
                  </TableCell>
                  <TableCell className="text-right font-semibold">
                    {metric.total_sessoes}
                  </TableCell>
                  <TableCell className="text-right">
                    <span className={`font-semibold ${
                      metric.mensagens_por_sessao > 2 ? 'text-green-600' :
                      metric.mensagens_por_sessao > 1 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {metric.mensagens_por_sessao.toFixed(2)}
                    </span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        
        {userMessageMetrics.length === 0 && (
          <div className="h-[200px] flex items-center justify-center text-muted-foreground">
            Nenhuma mensagem de usuário encontrada
          </div>
        )}
      </CardContent>
    </Card>
  );
}