'use client';

import React, { useMemo } from 'react';
import TableMetricUserMessages from './table-metric-user-messages';
import MetricsScoreCard from './metrics-scorecard';
import MetricsScoreCardDAUMAU from './metrics-scorecard-dau-mau';

interface MetricsDashboardProps {
  whitelist?: { [groupName: string]: string[] };
  historyData: { [phoneNumber: string]: Record<string, unknown>[] };
}

export interface FlatMessage {
  user_id: string;
  group_name: string;
  id: string;
  date: string;
  session_id: string;
  time_since_last_message: number | null;
  name: string | null;
  otid: string;
  sender_id: string | null;
  step_id: string;
  is_err: boolean | null;
  model_name: string | null;
  finish_reason: string | null;
  avg_logprobs: number | null;
  usage_metadata: Record<string, unknown>;
  message_type: string;
  content: string;
  tool_call: Record<string, unknown> | null;
  tool_return: Record<string, unknown> | null;
  status: string | null;
  tool_call_id: string | null;
  stdout: string | null;
  stderr: string | null;
}

export default function MetricsDashboard({ whitelist, historyData }: MetricsDashboardProps) {
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

  // Flatten all messages into a single array with original field names
  const flatMessages = useMemo(() => {
    const messages: FlatMessage[] = [];
    
    Object.entries(historyData).forEach(([phoneNumber, userMessages]) => {
      const group = phoneToGroup[phoneNumber] || 'Sem Grupo';
      
      userMessages.forEach(msg => {
        // Use original date without timezone conversion
        const normalizedDate = String(msg.date) || '';

        messages.push({
          user_id: phoneNumber,
          group_name: group,
          id: String(msg.id) || '',
          date: normalizedDate,
          session_id: String(msg.session_id) || '',
          time_since_last_message: typeof msg.time_since_last_message === 'number' ? msg.time_since_last_message : null,
          name: typeof msg.name === 'string' ? msg.name : null,
          otid: String(msg.otid) || '',
          sender_id: typeof msg.sender_id === 'string' ? msg.sender_id : null,
          step_id: String(msg.step_id) || '',
          is_err: typeof msg.is_err === 'boolean' ? msg.is_err : null,
          model_name: typeof msg.model_name === 'string' ? msg.model_name : null,
          finish_reason: typeof msg.finish_reason === 'string' ? msg.finish_reason : null,
          avg_logprobs: typeof msg.avg_logprobs === 'number' ? msg.avg_logprobs : null,
          usage_metadata: (typeof msg.usage_metadata === 'object' && msg.usage_metadata !== null) ? msg.usage_metadata as Record<string, unknown> : {},
          message_type: String(msg.message_type) || '',
          content: String(msg.content) || '',
          tool_call: (typeof msg.tool_call === 'object') ? msg.tool_call as Record<string, unknown> | null : null,
          tool_return: (typeof msg.tool_return === 'object') ? msg.tool_return as Record<string, unknown> | null : null,
          status: typeof msg.status === 'string' ? msg.status : null,
          tool_call_id: typeof msg.tool_call_id === 'string' ? msg.tool_call_id : null,
          stdout: typeof msg.stdout === 'string' ? msg.stdout : null,
          stderr: typeof msg.stderr === 'string' ? msg.stderr : null
        });
      });
    });
    
    return messages.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }, [historyData, phoneToGroup]);


  return (
    <div className="space-y-6">
      <MetricsScoreCard flatMessages={flatMessages} />
      <MetricsScoreCardDAUMAU flatMessages={flatMessages} />
      <TableMetricUserMessages flatMessages={flatMessages} />
    </div>
  );
}