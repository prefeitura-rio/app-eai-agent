'use client';

import React, { useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import { BarChart3 } from 'lucide-react';
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
  const [isModalOpen, setIsModalOpen] = useState(false);

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
    
    return result;
  }, [flatMessages]);

  // Transform data for chart
  const chartData = useMemo(() => {
    // Get all unique dates and sort them
    const allDates = [...new Set(userMessageMetrics.map(m => m.date))].sort();
    
    // Get all unique groups
    const allGroups = [...new Set(userMessageMetrics.map(m => m.group_name))];
    
    // Create chart data structure
    return allDates.map(date => {
      const dataPoint: any = { date: formatDate(date) };
      
      allGroups.forEach(group => {
        const metric = userMessageMetrics.find(m => m.date === date && m.group_name === group);
        dataPoint[group] = metric ? Number(metric.mensagens_por_sessao.toFixed(2)) : 0;
      });
      
      return dataPoint;
    });
  }, [userMessageMetrics]);

  // Colors for different groups
  const groupColors = [
    '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#d084d0', 
    '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57'
  ];


  const allGroups = [...new Set(userMessageMetrics.map(m => m.group_name))];

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Mensagens por Sessão - Análise Temporal</CardTitle>
          <p className="text-sm text-muted-foreground">
            Evolução das mensagens por sessão ao longo do tempo por grupo
          </p>
        </div>
        
        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <DialogTrigger asChild>
            <Button variant="ghost" size="sm">
              <BarChart3 className="h-4 w-4" />
            </Button>
          </DialogTrigger>
          <DialogContent 
            className="overflow-hidden p-6" 
            style={{ 
              width: '95vw', 
              maxWidth: '95vw', 
              height: '95vh', 
              maxHeight: '95vh' 
            }}
          >
            <DialogHeader className="pb-4">
              <DialogTitle>Dados Detalhados - Métricas por Grupo e Data</DialogTitle>
            </DialogHeader>
            <div className="overflow-auto" style={{ height: 'calc(95vh - 120px)' }}>
              {isModalOpen && (
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
              )}
            </div>
          </DialogContent>
        </Dialog>
      </CardHeader>
      
      <CardContent>
        {chartData.length > 0 ? (
          <ChartContainer
            config={{}}
            className="h-[400px] w-full"
          >
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  label={{ value: 'Mensagens/Sessão', angle: -90, position: 'insideLeft' }}
                  tick={{ fontSize: 12 }}
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Legend />
                {allGroups.map((group, index) => (
                  <Line
                    key={group}
                    type="monotone"
                    dataKey={group}
                    stroke={groupColors[index % groupColors.length]}
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    connectNulls={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>
        ) : (
          <div className="h-[400px] flex items-center justify-center text-muted-foreground">
            Nenhum dado disponível para exibir o gráfico
          </div>
        )}
      </CardContent>
    </Card>
  );
}