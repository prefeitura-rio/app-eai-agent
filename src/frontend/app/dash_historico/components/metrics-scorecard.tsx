'use client';

import React, { useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Users, MessageSquare, Timer, Table } from 'lucide-react';
import { FlatMessage } from './dashboard';
import TableMessages from './table-messages';

interface MetricsScoreCardProps {
  flatMessages: FlatMessage[];
}

export default function MetricsScoreCard({ flatMessages }: MetricsScoreCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Calculate key metrics
  const metrics = useMemo(() => {
    const distinctUsers = new Set(flatMessages.map(msg => msg.user_id)).size;
    const totalMessages = flatMessages.length;
    const distinctSessions = new Set(flatMessages.map(msg => msg.session_id)).size;

    return {
      distinctUsers,
      totalMessages,
      distinctSessions
    };
  }, [flatMessages]);

  const MetricCard = ({ 
    title, 
    value, 
    icon: Icon, 
    description 
  }: { 
    title: string; 
    value: number; 
    icon: any; 
    description: string;
  }) => (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value.toLocaleString('pt-BR')}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 flex-1">
          <MetricCard
            title="Usuários Únicos"
            value={metrics.distinctUsers}
            icon={Users}
            description="Total de usuários distintos"
          />
          
          <MetricCard
            title="Total de Mensagens"
            value={metrics.totalMessages}
            icon={MessageSquare}
            description="Todas as mensagens do período"
          />
          
          <MetricCard
            title="Sessões Únicas"
            value={metrics.distinctSessions}
            icon={Timer}
            description="Total de sessões distintas"
          />
        </div>

        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <DialogTrigger asChild>
            <Button variant="ghost" size="sm" className="ml-4">
              <Table className="h-4 w-4" />
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-[98vw] max-h-[95vh] overflow-hidden">
            <DialogHeader>
              <DialogTitle>Tabela de Mensagens - Dados Completos</DialogTitle>
            </DialogHeader>
            <div className="overflow-auto max-h-[calc(95vh-120px)]">
              <TableMessages flatMessages={flatMessages} />
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}