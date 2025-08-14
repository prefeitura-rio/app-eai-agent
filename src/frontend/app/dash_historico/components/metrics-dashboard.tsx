'use client';

import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';
import { CalculatedMetrics } from './metrics-calculator';
import { BarChart3, MessageSquare, DollarSign, TrendingUp, Users } from 'lucide-react';

interface MetricsDashboardProps {
  metrics: CalculatedMetrics;
  whitelist?: { [groupName: string]: string[] };
  historyData: { [phoneNumber: string]: any[] };
}

export default function MetricsDashboard({ metrics, whitelist, historyData }: MetricsDashboardProps) {
  // Create phone to group mapping
  const phoneToGroup: { [phone: string]: string } = useMemo(() => {
    const mapping: { [phone: string]: string } = {};
    if (whitelist) {
      Object.entries(whitelist).forEach(([groupName, phones]) => {
        phones.forEach(phone => {
          mapping[phone] = groupName;
        });
      });
    }
    return mapping;
  }, [whitelist]);

  // Format large numbers function
  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  // Process efficiency data
  const efficiencyData = useMemo(() => {
    const messagesByDateAndGroup: Map<string, Map<string, any[]>> = new Map();
    
    Object.entries(historyData).forEach(([phoneNumber, messages]) => {
      const group = phoneToGroup[phoneNumber] || 'Sem Grupo';
      
      messages.forEach(message => {
        if (message.date) {
          const messageDate = new Date(message.date);
          // Convert to São Paulo timezone (UTC-3)
          const saoPauloDate = new Date(messageDate.getTime() - (3 * 60 * 60 ));
          const dateKey = saoPauloDate.toISOString().split('T')[0];
          
          if (!messagesByDateAndGroup.has(dateKey)) {
            messagesByDateAndGroup.set(dateKey, new Map());
          }
          
          if (!messagesByDateAndGroup.get(dateKey)!.has(group)) {
            messagesByDateAndGroup.get(dateKey)!.set(group, []);
          }
          
          messagesByDateAndGroup.get(dateKey)!.get(group)!.push({ ...message, phoneNumber });
        }
      });
    });

    const result: any[] = [];
    const groupColors: { [key: string]: string } = {};
    let colorIndex = 0;
    const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0'];

    messagesByDateAndGroup.forEach((groupsOnDate, dateKey) => {
      const dataPoint: any = { date: dateKey };
      
      groupsOnDate.forEach((messages, group) => {
        if (!groupColors[group]) {
          groupColors[group] = colors[colorIndex % colors.length];
          colorIndex++;
        }

        const sessionGroups: { [sessionId: string]: any[] } = {};
        messages.forEach(msg => {
          const sessionId = msg.session_id || 'default';
          if (!sessionGroups[sessionId]) {
            sessionGroups[sessionId] = [];
          }
          sessionGroups[sessionId].push(msg);
        });

        const sessions = Object.values(sessionGroups);
        const avgMessagesPerSession = sessions.length > 0 ? 
          sessions.reduce((sum, session) => sum + session.length, 0) / sessions.length : 0;
        
        dataPoint[group] = sessions.length > 0 ? avgMessagesPerSession / sessions.length : 0;
      });
      
      result.push(dataPoint);
    });

    return { data: result.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()), colors: groupColors };
  }, [historyData, phoneToGroup]);

  // Process message count data
  const messageCountData = useMemo(() => {
    const messageCountByDateAndGroup: Map<string, Map<string, number>> = new Map();
    
    Object.entries(historyData).forEach(([phoneNumber, messages]) => {
      const group = phoneToGroup[phoneNumber] || 'Sem Grupo';
      
      messages.forEach(message => {
        if (message.date && (message.message_type === 'user_message' || message.message_type === 'assistant_message')) {
          const messageDate = new Date(message.date);
          // Convert to São Paulo timezone (UTC-3)
          const saoPauloDate = new Date(messageDate.getTime() - (3 * 60 * 60 * 1000));
          const dateKey = saoPauloDate.toISOString().split('T')[0];
          
          if (!messageCountByDateAndGroup.has(dateKey)) {
            messageCountByDateAndGroup.set(dateKey, new Map());
          }
          
          if (!messageCountByDateAndGroup.get(dateKey)!.has(group)) {
            messageCountByDateAndGroup.get(dateKey)!.set(group, 0);
          }
          
          messageCountByDateAndGroup.get(dateKey)!.set(
            group, 
            messageCountByDateAndGroup.get(dateKey)!.get(group)! + 1
          );
        }
      });
    });

    const result: any[] = [];
    const groupColors: { [key: string]: string } = {};
    let colorIndex = 0;
    const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0'];

    messageCountByDateAndGroup.forEach((groupsOnDate, dateKey) => {
      const dataPoint: any = { date: dateKey };
      
      groupsOnDate.forEach((totalMessages, group) => {
        if (!groupColors[group]) {
          groupColors[group] = colors[colorIndex % colors.length];
          colorIndex++;
        }
        dataPoint[group] = totalMessages;
      });
      
      result.push(dataPoint);
    });

    return { data: result.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()), colors: groupColors };
  }, [historyData, phoneToGroup]);

  // Process model calls data
  const modelCallsData = useMemo(() => {
    const modelCallsByDateAndGroup: Map<string, Map<string, number>> = new Map();
    
    Object.entries(historyData).forEach(([phoneNumber, messages]) => {
      const group = phoneToGroup[phoneNumber] || 'Sem Grupo';
      
      messages.forEach(message => {
        if (message.date && message.model_name && message.usage_metadata) {
          const messageDate = new Date(message.date);
          // Convert to São Paulo timezone (UTC-3)
          const saoPauloDate = new Date(messageDate.getTime() - (3 * 60 * 60 * 1000));
          const dateKey = saoPauloDate.toISOString().split('T')[0];
          
          if (!modelCallsByDateAndGroup.has(dateKey)) {
            modelCallsByDateAndGroup.set(dateKey, new Map());
          }
          
          if (!modelCallsByDateAndGroup.get(dateKey)!.has(group)) {
            modelCallsByDateAndGroup.get(dateKey)!.set(group, 0);
          }
          
          modelCallsByDateAndGroup.get(dateKey)!.set(
            group, 
            modelCallsByDateAndGroup.get(dateKey)!.get(group)! + 1
          );
        }
      });
    });

    const result: any[] = [];
    const groupColors: { [key: string]: string } = {};
    let colorIndex = 0;
    const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0'];

    modelCallsByDateAndGroup.forEach((groupsOnDate, dateKey) => {
      const dataPoint: any = { date: dateKey };
      
      groupsOnDate.forEach((totalCalls, group) => {
        if (!groupColors[group]) {
          groupColors[group] = colors[colorIndex % colors.length];
          colorIndex++;
        }
        dataPoint[group] = totalCalls;
      });
      
      result.push(dataPoint);
    });

    return { data: result.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()), colors: groupColors };
  }, [historyData, phoneToGroup]);

  // Process tokens data
  const tokensData = useMemo(() => {
    const tokensByDateAndGroup: Map<string, Map<string, number>> = new Map();
    
    Object.entries(historyData).forEach(([phoneNumber, messages]) => {
      const group = phoneToGroup[phoneNumber] || 'Sem Grupo';
      
      messages.forEach(message => {
        if (message.date && message.model_name && message.usage_metadata) {
          const messageDate = new Date(message.date);
          // Convert to São Paulo timezone (UTC-3)
          const saoPauloDate = new Date(messageDate.getTime() - (3 * 60 * 60 * 1000));
          const dateKey = saoPauloDate.toISOString().split('T')[0];
          
          if (!tokensByDateAndGroup.has(dateKey)) {
            tokensByDateAndGroup.set(dateKey, new Map());
          }
          
          if (!tokensByDateAndGroup.get(dateKey)!.has(group)) {
            tokensByDateAndGroup.get(dateKey)!.set(group, 0);
          }
          
          const usage = message.usage_metadata;
          const totalTokens = (usage.prompt_token_count || 0) + 
                             (usage.candidates_token_count || 0) + 
                             (usage.thoughts_token_count || 0) + 
                             (usage.cached_content_token_count || 0);
          
          tokensByDateAndGroup.get(dateKey)!.set(
            group, 
            tokensByDateAndGroup.get(dateKey)!.get(group)! + totalTokens
          );
        }
      });
    });

    const result: any[] = [];
    const groupColors: { [key: string]: string } = {};
    let colorIndex = 0;
    const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0'];

    tokensByDateAndGroup.forEach((groupsOnDate, dateKey) => {
      const dataPoint: any = { date: dateKey };
      
      groupsOnDate.forEach((totalTokens, group) => {
        if (!groupColors[group]) {
          groupColors[group] = colors[colorIndex % colors.length];
          colorIndex++;
        }
        dataPoint[group] = totalTokens;
      });
      
      result.push(dataPoint);
    });

    return { data: result.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()), colors: groupColors };
  }, [historyData, phoneToGroup]);

  // Create chart configs
  const createChartConfig = (colors: { [key: string]: string }): ChartConfig => {
    const config: ChartConfig = {};
    Object.entries(colors).forEach(([group, color]) => {
      config[group] = {
        label: group,
        color: color,
      };
    });
    return config;
  };

  const renderTimeSeriesChart = (
    data: any[], 
    colors: { [key: string]: string }, 
    yAxisFormatter?: (value: any) => string,
    chartType?: 'efficiency' | 'messages' | 'calls' | 'tokens'
  ) => {
    const groups = Object.keys(colors);
    
    // Calculate additional analytics
    const getAnalytics = (payload: any[], label: string) => {
      const totalForDay = payload.reduce((sum, entry) => sum + entry.value, 0);
      const avgValue = totalForDay / payload.length;
      
      // Get previous day data for comparison
      const currentIndex = data.findIndex(d => d.date === label);
      const previousDay = currentIndex > 0 ? data[currentIndex - 1] : null;
      
      let trends: { [key: string]: number } = {};
      if (previousDay) {
        payload.forEach(entry => {
          const prevValue = previousDay[entry.dataKey] || 0;
          const change = ((entry.value - prevValue) / prevValue) * 100;
          trends[entry.dataKey] = change;
        });
      }
      
      return { totalForDay, avgValue, trends };
    };
    
    return (
      <ChartContainer config={createChartConfig(colors)} className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' })}
              className="text-xs"
            />
            <YAxis 
              tickFormatter={yAxisFormatter || ((value) => value.toString())}
              className="text-xs"
            />
            <ChartTooltip 
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  const analytics = getAnalytics(payload, label);
                  
                  return (
                    <div className="rounded-lg border bg-background p-3 shadow-lg min-w-[280px]">
                      <div className="grid gap-3">
                        <div className="border-b pb-2">
                          <div className="font-semibold text-sm">
                            {new Date(label).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Total: {yAxisFormatter ? yAxisFormatter(analytics.totalForDay) : analytics.totalForDay.toLocaleString()}
                            {payload.length > 1 && ` • Média: ${yAxisFormatter ? yAxisFormatter(analytics.avgValue) : analytics.avgValue.toFixed(1)}`}
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          {payload.map((entry: any) => {
                            const trend = analytics.trends[entry.dataKey];
                            const trendIcon = trend > 0 ? '↗️' : trend < 0 ? '↘️' : '➡️';
                            const trendColor = trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-gray-500';
                            
                            return (
                              <div key={entry.dataKey} className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <div 
                                    className="h-3 w-3 rounded-full border border-white shadow-sm" 
                                    style={{ backgroundColor: entry.color }}
                                  />
                                  <span className="font-medium text-sm">
                                    {entry.dataKey}
                                  </span>
                                </div>
                                
                                <div className="text-right">
                                  <div className="font-semibold text-sm">
                                    {yAxisFormatter ? yAxisFormatter(entry.value) : entry.value}
                                  </div>
                                  {!isNaN(trend) && (
                                    <div className={`text-xs ${trendColor} flex items-center gap-1`}>
                                      <span>{trendIcon}</span>
                                      <span>{Math.abs(trend).toFixed(1)}%</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                        
                        {payload.length > 1 && (
                          <div className="border-t pt-2 text-xs text-muted-foreground">
                            <div className="flex justify-between">
                              <span>Maior: {payload.reduce((max, p) => p.value > max.value ? p : max).dataKey}</span>
                              <span>Menor: {payload.reduce((min, p) => p.value < min.value ? p : min).dataKey}</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            {groups.map((group) => (
              <Line
                key={group}
                type="monotone"
                dataKey={group}
                stroke={colors[group]}
                strokeWidth={2}
                dot={{ fill: colors[group], strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, strokeWidth: 2 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </ChartContainer>
    );
  };

  return (
    <div className="space-y-6">
      {/* Overall Metrics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Telefones</p>
                <p className="text-xl font-bold">{metrics.overall.totalPhones}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Sessões</p>
                <p className="text-xl font-bold">{metrics.overall.totalSessions}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Mensagens</p>
                <p className="text-xl font-bold">{metrics.overall.totalMessages}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Msgs/Sessão</p>
                <p className="text-xl font-bold">{metrics.overall.avgMessagesPerSession.toFixed(1)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Custo Total</p>
                <p className="text-xl font-bold">${metrics.overall.totalCost.toFixed(3)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Engajamento</p>
                <p className="text-xl font-bold">{metrics.overall.engagementRate.toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 gap-6">
        {/* First Row - Messages Charts Side by Side */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Messages Efficiency Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Evolução da Eficiência de Mensagens ao Longo do Tempo
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Série temporal da eficiência de mensagens por grupo (linhas coloridas por grupo)
              </p>
            </CardHeader>
            <CardContent>
              {efficiencyData.data.length > 0 ? (
                renderTimeSeriesChart(efficiencyData.data, efficiencyData.colors, (value) => value.toFixed(1), 'efficiency')
              ) : (
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  Nenhum dado disponível
                </div>
              )}
            </CardContent>
          </Card>

          {/* Messages Count Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Evolução do Número de Mensagens ao Longo do Tempo
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Série temporal do total de mensagens (user + assistant) por grupo
              </p>
            </CardHeader>
            <CardContent>
              {messageCountData.data.length > 0 ? (
                renderTimeSeriesChart(messageCountData.data, messageCountData.colors, undefined, 'messages')
              ) : (
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  Nenhum dado disponível
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Second Row - Model Calls and Tokens Side by Side */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Model Calls Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Evolução de Chamadas ao Modelo ao Longo do Tempo
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Série temporal do total de chamadas aos modelos por grupo
              </p>
            </CardHeader>
            <CardContent>
              {modelCallsData.data.length > 0 ? (
                renderTimeSeriesChart(modelCallsData.data, modelCallsData.colors, undefined, 'calls')
              ) : (
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  Nenhum dado disponível
                </div>
              )}
            </CardContent>
          </Card>

          {/* Tokens Usage Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Evolução do Consumo de Tokens ao Longo do Tempo
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Série temporal do total de tokens consumidos por grupo
              </p>
            </CardHeader>
            <CardContent>
              {tokensData.data.length > 0 ? (
                renderTimeSeriesChart(tokensData.data, tokensData.colors, formatNumber, 'tokens')
              ) : (
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  Nenhum dado disponível
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}