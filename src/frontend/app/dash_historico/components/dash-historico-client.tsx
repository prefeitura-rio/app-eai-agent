'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { RefreshCw, Users, Phone, BarChart3, Loader2 } from 'lucide-react';
import { useHeader } from '@/app/contexts/HeaderContext';
import { useAuth } from '@/app/contexts/AuthContext';
import { API_BASE_URL } from '@/app/components/config';
import { toast } from 'sonner';
import MetricsDashboard from './dashboard';

interface WhitelistData {
  [groupName: string]: string[];
}

interface DashHistoricoClientProps {
  whitelist: WhitelistData;
}

interface HistoryData {
  [phoneNumber: string]: any[];
}

export default function DashHistoricoClient({ whitelist }: DashHistoricoClientProps) {
  const { setTitle, setSubtitle } = useHeader();
  const { token } = useAuth();
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null);
  const [selectedPhones, setSelectedPhones] = useState<Set<string>>(new Set());
  const [searchTerm] = useState('');
  const [historyData, setHistoryData] = useState<HistoryData>({});
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [sessionTimeout, setSessionTimeout] = useState<number>(3600); // 1 hour default

  useEffect(() => {
    setTitle('Dashboard Histórico');
    setSubtitle('Análise de histórico de conversas por grupos e telefones');
  }, [setTitle, setSubtitle]);

  // Reset selected phones when group changes
  useEffect(() => {
    setSelectedPhones(new Set());
  }, [selectedGroup]);

  const fetchHistory = async () => {
    if (selectedPhones.size === 0) {
      toast.error('Selecione pelo menos um telefone');
      return;
    }

    setIsLoadingHistory(true);
    
    try {
      const phoneNumbers = Array.from(selectedPhones);
      const response = await fetch(`${API_BASE_URL}/api/v1/eai-gateway/history/bulk`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_ids: phoneNumbers,
          session_timeout_seconds: sessionTimeout,
          use_whatsapp_format: true
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch history');
      }

      const data = await response.json();
      setHistoryData(data.data);
      toast.success(`Histórico carregado para ${phoneNumbers.length} telefone(s)`);
    } catch (error) {
      console.error('Error fetching history:', error);
      toast.error('Erro ao buscar histórico');
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const togglePhoneSelection = (phone: string) => {
    const newSelection = new Set(selectedPhones);
    if (newSelection.has(phone)) {
      newSelection.delete(phone);
    } else {
      newSelection.add(phone);
    }
    setSelectedPhones(newSelection);
  };


  const selectAllGroups = () => {
    const allPhones = Object.values(whitelist).flat();
    setSelectedPhones(new Set(allPhones));
  };

  const selectAllPhonesFromGroup = (groupName: string) => {
    const groupPhones = whitelist[groupName] || [];
    const newSelection = new Set(selectedPhones);
    groupPhones.forEach(phone => newSelection.add(phone));
    setSelectedPhones(newSelection);
  };

  const deselectAllPhonesFromGroup = (groupName: string) => {
    const groupPhones = whitelist[groupName] || [];
    const newSelection = new Set(selectedPhones);
    groupPhones.forEach(phone => newSelection.delete(phone));
    setSelectedPhones(newSelection);
  };

  const isGroupFullySelected = (groupName: string) => {
    const groupPhones = whitelist[groupName] || [];
    return groupPhones.length > 0 && groupPhones.every(phone => selectedPhones.has(phone));
  };

  const isGroupPartiallySelected = (groupName: string) => {
    const groupPhones = whitelist[groupName] || [];
    return groupPhones.some(phone => selectedPhones.has(phone)) && !isGroupFullySelected(groupName);
  };

  const toggleGroupSelection = (groupName: string) => {
    if (isGroupFullySelected(groupName)) {
      deselectAllPhonesFromGroup(groupName);
    } else {
      selectAllPhonesFromGroup(groupName);
    }
  };

  const clearSelection = () => {
    setSelectedPhones(new Set());
  };

  const groupNames = Object.keys(whitelist);
  const totalGroups = groupNames.length;
  const totalPhones = Object.values(whitelist).reduce((acc, phones) => acc + phones.length, 0);

  const filteredGroups = groupNames.filter(groupName =>
    groupName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedGroupPhones = selectedGroup ? whitelist[selectedGroup] || [] : [];
  
  // Filter history data by selected phones
  const filteredHistoryData = useMemo(() => {
    if (selectedPhones.size === 0) {
      return historyData;
    }
    
    const filtered: HistoryData = {};
    selectedPhones.forEach(phone => {
      if (historyData[phone]) {
        filtered[phone] = historyData[phone];
      }
    });
    return filtered;
  }, [historyData, selectedPhones]);

  // Calculate metrics from filtered history data
  const hasHistoryData = Object.keys(historyData).length > 0;

  return (
    <div className="grid md:grid-cols-[300px_1fr] gap-6 h-[calc(100vh-200px)] max-h-screen">
      {/* Left Panel - Groups Accordion */}
      <Card className="flex flex-col h-full overflow-hidden">
        <CardHeader className="flex-shrink-0">
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Grupos ({totalGroups})
          </CardTitle>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">
              Total de telefones: {totalPhones}
            </span>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" onClick={() => window.location.reload()} size="icon">
                  <RefreshCw className="h-4 w-4 text-primary" />
                </Button>
              </TooltipTrigger>
              <TooltipContent><p>Atualizar</p></TooltipContent>
            </Tooltip>
          </div>
        </CardHeader>
        
        <div className="flex-shrink-0 p-4 space-y-3">
          <div className="space-y-3">
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Timeout de Sessão
              </label>
              <div className="flex gap-1 mb-2">
                {[
                  { label: '1h', value: 3600 },
                  { label: '6h', value: 21600 },
                  { label: '12h', value: 43200 },
                  { label: '24h', value: 86400 }
                ].map(preset => (
                  <Button
                    key={preset.value}
                    variant={sessionTimeout === preset.value ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSessionTimeout(preset.value)}
                    className="text-xs h-7 px-2"
                  >
                    {preset.label}
                  </Button>
                ))}
              </div>
              <Input
                type="number"
                value={sessionTimeout}
                onChange={(e) => setSessionTimeout(Number(e.target.value))}
                placeholder="43200"
                className="text-xs h-8"
                min="60"
                max="86400"
              />
              <p className="text-xs text-muted-foreground mt-1">
                {Math.floor(sessionTimeout / 3600)}h {Math.floor((sessionTimeout % 3600) / 60)}min
              </p>
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={clearSelection}
                disabled={selectedPhones.size === 0}
                className="text-xs flex-1"
              >
                Limpar Seleção
              </Button>
              <Button 
                onClick={fetchHistory}
                disabled={selectedPhones.size === 0 || isLoadingHistory}
                size="sm"
                className="text-xs flex-1"
              >
                {isLoadingHistory ? (
                  <>
                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                    Carregando...
                  </>
                ) : (
                  <>
                    <BarChart3 className="h-3 w-3 mr-1" />
                    Buscar Histórico
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>

        <CardContent className="flex-1 overflow-y-auto p-4 min-h-0">
          <div className="space-y-3 mb-4">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={selectAllGroups}
              className="text-xs w-full"
            >
              Selecionar Todos os Grupos
            </Button>
            <p className="text-xs text-muted-foreground">
              {selectedPhones.size} telefones selecionados
            </p>
          </div>
          
          <Accordion type="single" collapsible className="w-full">
            {filteredGroups.length > 0 ? (
              filteredGroups.map((groupName) => (
                <AccordionItem key={groupName} value={groupName} className="border-none w-full" style={{ width: '100%', maxWidth: '100%' }}>
                  <div className="flex items-center gap-2 w-full" style={{ width: '100%' }}>
                    <Checkbox
                      checked={isGroupFullySelected(groupName)}
                      {...(isGroupPartiallySelected(groupName) ? { indeterminate: true } : {})}
                      onCheckedChange={() => toggleGroupSelection(groupName)}
                      className="flex-shrink-0 w-4 h-4"
                    />
                    <AccordionTrigger 
                      className={`flex h-16 items-center justify-between gap-3 rounded-lg px-3 py-3 text-sm font-medium transition-colors hover:no-underline ${
                        selectedGroup === groupName 
                          ? 'bg-primary text-primary-foreground hover:bg-primary/90' 
                          : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                      }`}
                      style={{ 
                        width: '234px', // 266px container - 16px checkbox - 8px gap - 8px padding = 234px
                        maxWidth: '234px',
                        minWidth: '234px',
                        flexShrink: 0
                      }}
                      onClick={() => setSelectedGroup(groupName)}
                    >
                      <div className="flex items-center justify-between w-full min-w-0">
                        <div className="flex-1 min-w-0 text-left pr-2">
                          <p className="font-medium break-words leading-tight">{groupName}</p>
                          <div className="text-xs opacity-70 h-4 mt-1">
                            {(isGroupFullySelected(groupName) || isGroupPartiallySelected(groupName)) && (
                              <span>
                                {whitelist[groupName].filter(phone => selectedPhones.has(phone)).length} selecionados
                              </span>
                            )}
                          </div>
                        </div>
                        <Badge variant="outline" className="ml-2 flex-shrink-0">
                          {whitelist[groupName].length}
                        </Badge>
                      </div>
                    </AccordionTrigger>
                  </div>
                  <AccordionContent className="pt-1">
                    <div className="space-y-3 pl-2">
                      {selectedGroup === groupName && (
                        <div className="space-y-1 max-h-96 overflow-y-auto">
                          {selectedGroupPhones.map((phone, index) => (
                            <div
                              key={index}
                              className={`flex items-center gap-2 p-2 rounded text-xs cursor-pointer transition-colors hover:bg-accent ${
                                selectedPhones.has(phone) ? 'bg-accent border border-primary' : 'border border-transparent'
                              }`}
                              onClick={() => togglePhoneSelection(phone)}
                            >
                              <Checkbox 
                                checked={selectedPhones.has(phone)}
                                onChange={() => togglePhoneSelection(phone)}
                                className="pointer-events-none h-3 w-3"
                              />
                              <Phone className="h-3 w-3 text-muted-foreground" />
                              <span className="font-mono flex-1">+{phone}</span>
                              {historyData[phone] && (
                                <Badge variant="secondary" className="text-xs px-1 py-0">
                                  {historyData[phone].length}
                                </Badge>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))
            ) : (
              <div className="text-center py-4 text-muted-foreground text-sm">
                Nenhum grupo encontrado
              </div>
            )}
          </Accordion>
        </CardContent>
      </Card>

      {/* Right Panel - Dashboard */}
      <div className="h-full overflow-y-auto max-h-full">
        <div className="space-y-6 p-6">
          {hasHistoryData ? (
            <>
              {selectedPhones.size > 0 && (
                <div className="bg-accent/50 border border-accent rounded-lg p-3 mb-4">
                  <p className="text-sm text-muted-foreground">
                    Mostrando métricas para {selectedPhones.size} telefone{selectedPhones.size !== 1 ? 's' : ''} selecionado{selectedPhones.size !== 1 ? 's' : ''}
                  </p>
                </div>
              )}
              <MetricsDashboard whitelist={whitelist} historyData={filteredHistoryData} />
            </>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-muted-foreground">
                <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">Dashboard de Métricas</p>
                <p className="text-sm">Selecione telefones e obtenha o histórico para visualizar as métricas</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}