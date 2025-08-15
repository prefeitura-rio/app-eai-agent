'use client';

import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { FlatMessage } from './dashboard';
import { extractDateKey } from '@/app/utils/date-formatter';

interface MetricsScoreCardDAUMAUProps {
  flatMessages: FlatMessage[];
}

export default function MetricsScoreCardDAUMAU({ flatMessages }: MetricsScoreCardDAUMAUProps) {

  // Calculate DAU (Daily Active Users) and MAU (Monthly Active Users)
  const dauMauMetrics = useMemo(() => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    const lastMonth = new Date(currentYear, currentMonth - 1);
    
    // Get unique users for today and yesterday (DAU)
    const todayUsers = new Set<string>();
    const yesterdayUsers = new Set<string>();
    
    // Get unique users for current and last month (MAU)
    const currentMonthUsers = new Set<string>();
    const lastMonthUsers = new Set<string>();
    
    // Get unique sessions for current period
    const totalSessions = new Set<string>();
    let totalSessionLength = 0;
    let sessionCount = 0;
    
    flatMessages.forEach(msg => {
      if (msg.date && msg.user_id) {
        const msgDate = new Date(msg.date);
        const dateKey = extractDateKey(msg.date);
        
        // DAU calculation
        if (dateKey === extractDateKey(today.toISOString())) {
          todayUsers.add(msg.user_id);
        }
        if (dateKey === extractDateKey(yesterday.toISOString())) {
          yesterdayUsers.add(msg.user_id);
        }
        
        // MAU calculation
        if (msgDate.getMonth() === currentMonth && msgDate.getFullYear() === currentYear) {
          currentMonthUsers.add(msg.user_id);
        }
        if (msgDate.getMonth() === lastMonth.getMonth() && msgDate.getFullYear() === lastMonth.getFullYear()) {
          lastMonthUsers.add(msg.user_id);
        }
        
        // Sessions calculation
        if (msg.session_id) {
          totalSessions.add(msg.session_id);
          
          // Estimate session length (simplified)
          if (msg.time_since_last_message && msg.time_since_last_message > 0) {
            totalSessionLength += msg.time_since_last_message;
            sessionCount++;
          }
        }
      }
    });
    
    const dau = todayUsers.size;
    const dauYesterday = yesterdayUsers.size;
    const dauChange = dauYesterday > 0 ? ((dau - dauYesterday) / dauYesterday) * 100 : 0;
    
    const mau = currentMonthUsers.size;
    const mauLastMonth = lastMonthUsers.size;
    const mauChange = mauLastMonth > 0 ? ((mau - mauLastMonth) / mauLastMonth) * 100 : 0;
    
    const sessionsPerUser = dau > 0 ? totalSessions.size / dau : 0;
    const avgSessionLength = sessionCount > 0 ? totalSessionLength / sessionCount : 0;
    
    return {
      dau,
      dauChange,
      mau,
      mauChange,
      sessionsPerUser,
      avgSessionLength
    };
  }, [flatMessages]);

  const MetricCard = ({ 
    title, 
    value, 
    change, 
    unit = '',
    showTrend = true 
  }: { 
    title: string; 
    value: number | string; 
    change?: number; 
    unit?: string;
    showTrend?: boolean;
  }) => {
    const getTrendIcon = () => {
      if (!showTrend || change === undefined) return <Minus className="h-4 w-4 text-gray-400" />;
      if (change > 0) return <TrendingUp className="h-4 w-4 text-green-500" />;
      if (change < 0) return <TrendingDown className="h-4 w-4 text-red-500" />;
      return <Minus className="h-4 w-4 text-gray-400" />;
    };
    
    const getTrendColor = () => {
      if (!showTrend || change === undefined) return 'text-gray-400';
      if (change > 0) return 'text-green-500';
      if (change < 0) return 'text-red-500';
      return 'text-gray-400';
    };

    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {typeof value === 'number' ? value.toLocaleString('pt-BR') : value}{unit}
          </div>
          {showTrend && (
            <div className={`flex items-center text-xs ${getTrendColor()}`}>
              {getTrendIcon()}
              <span className="ml-1">
                {change !== undefined ? `${Math.abs(change).toFixed(2)}%` : '—'}
              </span>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <MetricCard
        title="DAU"
        value={dauMauMetrics.dau}
        change={dauMauMetrics.dauChange}
      />
      
      <MetricCard
        title="MAU"
        value={dauMauMetrics.mau}
        change={dauMauMetrics.mauChange}
      />
      
      <MetricCard
        title="Sessions Per User"
        value={dauMauMetrics.sessionsPerUser.toFixed(1)}
        change={undefined}
        showTrend={false}
      />
      
      <MetricCard
        title="Session Length"
        value={Math.round(dauMauMetrics.avgSessionLength)}
        unit="s"
        change={undefined}
        showTrend={false}
      />
    </div>
  );
}