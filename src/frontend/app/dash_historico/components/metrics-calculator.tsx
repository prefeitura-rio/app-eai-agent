'use client';

import { useMemo } from 'react';

interface Message {
  sender: string;
  content: string;
  timestamp: string;
  session_id?: string;
  cost?: number;
}

interface SessionMetrics {
  sessionId: string;
  phoneNumber: string;
  startTime: string;
  endTime: string;
  duration: number;
  messageCount: number;
  userMessages: number;
  agentMessages: number;
  avgResponseTime: number;
  totalCost: number;
}

interface EngagementMetrics {
  phoneNumber: string;
  firstInteraction: string;
  lastInteraction: string;
  totalSessions: number;
  returnedWithinWeek: boolean;
  daysBetweenFirstAndLast: number;
}

interface HistoryData {
  [phoneNumber: string]: Message[];
}

export interface CalculatedMetrics {
  sessions: SessionMetrics[];
  engagement: EngagementMetrics[];
  overall: {
    totalPhones: number;
    totalSessions: number;
    totalMessages: number;
    avgMessagesPerSession: number;
    avgCostPerSession: number;
    totalCost: number;
    engagementRate: number;
  };
}

export function useMetricsCalculator(historyData: HistoryData): CalculatedMetrics {
  return useMemo(() => {
    const sessions: SessionMetrics[] = [];
    const engagement: EngagementMetrics[] = [];
    
    let totalMessages = 0;
    let totalCost = 0;
    let returnedCount = 0;

    Object.entries(historyData).forEach(([phoneNumber, messages]) => {
      if (!messages || messages.length === 0) return;

      // Group messages by session_id
      const sessionGroups: { [sessionId: string]: Message[] } = {};
      messages.forEach(msg => {
        const sessionId = msg.session_id || 'default';
        if (!sessionGroups[sessionId]) {
          sessionGroups[sessionId] = [];
        }
        sessionGroups[sessionId].push(msg);
      });

      // Calculate session metrics
      Object.entries(sessionGroups).forEach(([sessionId, sessionMessages]) => {
        const sortedMessages = sessionMessages.sort((a, b) => 
          new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        );

        const userMessages = sortedMessages.filter(m => m.sender === 'user').length;
        const agentMessages = sortedMessages.filter(m => m.sender === 'assistant').length;
        
        const startTime = sortedMessages[0].timestamp;
        const endTime = sortedMessages[sortedMessages.length - 1].timestamp;
        const duration = new Date(endTime).getTime() - new Date(startTime).getTime();
        
        // Calculate average response time (time between user message and next agent message)
        let responseTimes: number[] = [];
        for (let i = 0; i < sortedMessages.length - 1; i++) {
          if (sortedMessages[i].sender === 'user' && sortedMessages[i + 1].sender === 'assistant') {
            const responseTime = new Date(sortedMessages[i + 1].timestamp).getTime() - 
                               new Date(sortedMessages[i].timestamp).getTime();
            responseTimes.push(responseTime);
          }
        }
        const avgResponseTime = responseTimes.length > 0 ? 
          responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length : 0;

        // Calculate session cost
        const sessionCost = sessionMessages.reduce((sum, msg) => sum + (msg.cost || 0), 0);

        sessions.push({
          sessionId,
          phoneNumber,
          startTime,
          endTime,
          duration,
          messageCount: sessionMessages.length,
          userMessages,
          agentMessages,
          avgResponseTime,
          totalCost: sessionCost,
        });

        totalMessages += sessionMessages.length;
        totalCost += sessionCost;
      });

      // Calculate engagement metrics
      const allMessages = messages.sort((a, b) => 
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      );
      
      const firstInteraction = allMessages[0].timestamp;
      const lastInteraction = allMessages[allMessages.length - 1].timestamp;
      const daysBetween = (new Date(lastInteraction).getTime() - new Date(firstInteraction).getTime()) / (1000 * 60 * 60 * 24);
      const returnedWithinWeek = daysBetween <= 7 && daysBetween > 0;
      
      if (returnedWithinWeek) returnedCount++;

      engagement.push({
        phoneNumber,
        firstInteraction,
        lastInteraction,
        totalSessions: Object.keys(sessionGroups).length,
        returnedWithinWeek,
        daysBetweenFirstAndLast: daysBetween,
      });
    });

    const totalPhones = Object.keys(historyData).length;
    const totalSessions = sessions.length;
    const avgMessagesPerSession = totalSessions > 0 ? totalMessages / totalSessions : 0;
    const avgCostPerSession = totalSessions > 0 ? totalCost / totalSessions : 0;
    const engagementRate = totalPhones > 0 ? (returnedCount / totalPhones) * 100 : 0;

    return {
      sessions,
      engagement,
      overall: {
        totalPhones,
        totalSessions,
        totalMessages,
        avgMessagesPerSession,
        avgCostPerSession,
        totalCost,
        engagementRate,
      },
    };
  }, [historyData]);
}