'use client';

import React, { useMemo } from 'react';
import TableMessages from './table-messages';
import TableMetricUserMessages from './table-metric-user-messages';
import MetricsScoreCard from './metrics-scorecard';
import MetricsScoreCardDAUMAU from './metrics-scorecard-dau-mau';

interface MetricsDashboardProps {
  whitelist?: { [groupName: string]: string[] };
  historyData: { [phoneNumber: string]: any[] };
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
  usage_metadata: any;
  message_type: string;
  content: string;
  tool_call: any;
  tool_return: any;
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
        let normalizedDate = msg.date || '';

        messages.push({
          user_id: phoneNumber,
          group_name: group,
          id: msg.id || '',
          date: normalizedDate,
          session_id: msg.session_id || '',
          time_since_last_message: msg.time_since_last_message,
          name: msg.name,
          otid: msg.otid || '',
          sender_id: msg.sender_id,
          step_id: msg.step_id || '',
          is_err: msg.is_err,
          model_name: msg.model_name,
          finish_reason: msg.finish_reason,
          avg_logprobs: msg.avg_logprobs,
          usage_metadata: msg.usage_metadata,
          message_type: msg.message_type || '',
          content: msg.content || '',
          tool_call: msg.tool_call,
          tool_return: msg.tool_return,
          status: msg.status,
          tool_call_id: msg.tool_call_id,
          stdout: msg.stdout,
          stderr: msg.stderr
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