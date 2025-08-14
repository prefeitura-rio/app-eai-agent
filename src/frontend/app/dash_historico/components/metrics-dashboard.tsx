'use client';

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CalculatedMetrics } from './metrics-calculator';
import { BarChart3, Clock, MessageSquare, DollarSign, TrendingUp, Users } from 'lucide-react';

interface MetricsDashboardProps {
  metrics: CalculatedMetrics;
}

export default function MetricsDashboard({ metrics }: MetricsDashboardProps) {
  const messagesChartRef = useRef<SVGSVGElement>(null);
  const engagementChartRef = useRef<SVGSVGElement>(null);
  const costChartRef = useRef<SVGSVGElement>(null);
  const responseTimeChartRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (metrics.sessions.length === 0) return;

    // Messages per session chart
    if (messagesChartRef.current) {
      drawMessagesChart();
    }

    // Engagement timeline chart
    if (engagementChartRef.current) {
      drawEngagementChart();
    }

    // Cost distribution chart
    if (costChartRef.current) {
      drawCostChart();
    }

    // Response time chart
    if (responseTimeChartRef.current) {
      drawResponseTimeChart();
    }
  }, [metrics]);

  const drawMessagesChart = () => {
    const svg = d3.select(messagesChartRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = 400 - margin.left - margin.right;
    const height = 200 - margin.bottom - margin.top;

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Group sessions by message count ranges
    const messageCounts = metrics.sessions.map(s => s.messageCount);
    const bins = d3.bin().thresholds(10)(messageCounts);

    const x = d3.scaleLinear()
      .domain(d3.extent(messageCounts) as [number, number])
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(bins, d => d.length) as number])
      .range([height, 0]);

    // Draw bars
    g.selectAll(".bar")
      .data(bins)
      .enter().append("rect")
      .attr("class", "bar")
      .attr("x", d => x(d.x0 as number))
      .attr("width", d => Math.max(0, x(d.x1 as number) - x(d.x0 as number) - 1))
      .attr("y", d => y(d.length))
      .attr("height", d => height - y(d.length))
      .attr("fill", "hsl(var(--primary))")
      .attr("opacity", 0.7);

    // Add axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x));

    g.append("g")
      .call(d3.axisLeft(y));

    // Add labels
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (height / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .text("Frequência");

    g.append("text")
      .attr("transform", `translate(${width / 2}, ${height + margin.bottom - 5})`)
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .text("Mensagens por Sessão");
  };

  const drawEngagementChart = () => {
    const svg = d3.select(engagementChartRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = 400 - margin.left - margin.right;
    const height = 200 - margin.bottom - margin.top;

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Engagement over time
    const engagementData = metrics.engagement.map(e => ({
      date: new Date(e.firstInteraction),
      returned: e.returnedWithinWeek ? 1 : 0
    })).sort((a, b) => a.date.getTime() - b.date.getTime());

    if (engagementData.length === 0) return;

    const x = d3.scaleTime()
      .domain(d3.extent(engagementData, d => d.date) as [Date, Date])
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([0, 1])
      .range([height, 0]);

    const line = d3.line<any>()
      .x(d => x(d.date))
      .y(d => y(d.returned))
      .curve(d3.curveStepAfter);

    g.append("path")
      .datum(engagementData)
      .attr("fill", "none")
      .attr("stroke", "hsl(var(--primary))")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Add dots
    g.selectAll(".dot")
      .data(engagementData)
      .enter().append("circle")
      .attr("class", "dot")
      .attr("cx", d => x(d.date))
      .attr("cy", d => y(d.returned))
      .attr("r", 3)
      .attr("fill", d => d.returned ? "hsl(var(--primary))" : "hsl(var(--muted))");

    // Add axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x).tickFormat(d3.timeFormat("%m/%d")));

    g.append("g")
      .call(d3.axisLeft(y).tickFormat(d => d === 1 ? "Retornou" : "Não retornou"));
  };

  const drawCostChart = () => {
    const svg = d3.select(costChartRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const width = 400 - margin.left - margin.right;
    const height = 200 - margin.bottom - margin.top;

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const costs = metrics.sessions.map(s => s.totalCost).filter(c => c > 0);
    if (costs.length === 0) return;

    const bins = d3.bin().thresholds(8)(costs);

    const x = d3.scaleLinear()
      .domain(d3.extent(costs) as [number, number])
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(bins, d => d.length) as number])
      .range([height, 0]);

    // Draw bars
    g.selectAll(".bar")
      .data(bins)
      .enter().append("rect")
      .attr("class", "bar")
      .attr("x", d => x(d.x0 as number))
      .attr("width", d => Math.max(0, x(d.x1 as number) - x(d.x0 as number) - 1))
      .attr("y", d => y(d.length))
      .attr("height", d => height - y(d.length))
      .attr("fill", "hsl(var(--destructive))")
      .attr("opacity", 0.7);

    // Add axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x).tickFormat(d => `$${d.toFixed(3)}`));

    g.append("g")
      .call(d3.axisLeft(y));

    // Add labels
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (height / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .text("Frequência");

    g.append("text")
      .attr("transform", `translate(${width / 2}, ${height + margin.bottom - 5})`)
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .text("Custo por Sessão ($)");
  };

  const drawResponseTimeChart = () => {
    const svg = d3.select(responseTimeChartRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const width = 400 - margin.left - margin.right;
    const height = 200 - margin.bottom - margin.top;

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const responseTimes = metrics.sessions
      .map(s => s.avgResponseTime / 1000) // Convert to seconds
      .filter(t => t > 0);

    if (responseTimes.length === 0) return;

    const bins = d3.bin().thresholds(10)(responseTimes);

    const x = d3.scaleLinear()
      .domain(d3.extent(responseTimes) as [number, number])
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(bins, d => d.length) as number])
      .range([height, 0]);

    // Draw bars
    g.selectAll(".bar")
      .data(bins)
      .enter().append("rect")
      .attr("class", "bar")
      .attr("x", d => x(d.x0 as number))
      .attr("width", d => Math.max(0, x(d.x1 as number) - x(d.x0 as number) - 1))
      .attr("y", d => y(d.length))
      .attr("height", d => height - y(d.length))
      .attr("fill", "hsl(var(--warning))")
      .attr("opacity", 0.7);

    // Add axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x).tickFormat(d => `${d.toFixed(1)}s`));

    g.append("g")
      .call(d3.axisLeft(y));

    // Add labels
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (height / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .text("Frequência");

    g.append("text")
      .attr("transform", `translate(${width / 2}, ${height + margin.bottom - 5})`)
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .text("Tempo de Resposta (s)");
  };

  const formatDuration = (ms: number) => {
    const hours = Math.floor(ms / (1000 * 60 * 60));
    const minutes = Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
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

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Distribuição de Mensagens por Sessão
            </CardTitle>
          </CardHeader>
          <CardContent>
            <svg ref={messagesChartRef} width="400" height="200"></svg>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Curva de Engajamento
            </CardTitle>
          </CardHeader>
          <CardContent>
            <svg ref={engagementChartRef} width="400" height="200"></svg>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              Distribuição de Custos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <svg ref={costChartRef} width="400" height="200"></svg>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Tempos de Resposta
            </CardTitle>
          </CardHeader>
          <CardContent>
            <svg ref={responseTimeChartRef} width="400" height="200"></svg>
          </CardContent>
        </Card>
      </div>

      {/* Sessions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Sessões Detalhadas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="max-h-96 overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-background">
                <tr className="border-b">
                  <th className="text-left p-2">Telefone</th>
                  <th className="text-left p-2">Duração</th>
                  <th className="text-center p-2">Mensagens</th>
                  <th className="text-center p-2">Usuário</th>
                  <th className="text-center p-2">Agente</th>
                  <th className="text-center p-2">Resp. Média</th>
                  <th className="text-center p-2">Custo</th>
                </tr>
              </thead>
              <tbody>
                {metrics.sessions.map((session, index) => (
                  <tr key={index} className="border-b hover:bg-accent">
                    <td className="p-2 font-mono text-xs">+{session.phoneNumber}</td>
                    <td className="p-2">{formatDuration(session.duration)}</td>
                    <td className="text-center p-2">
                      <Badge variant="outline">{session.messageCount}</Badge>
                    </td>
                    <td className="text-center p-2">{session.userMessages}</td>
                    <td className="text-center p-2">{session.agentMessages}</td>
                    <td className="text-center p-2">{(session.avgResponseTime / 1000).toFixed(1)}s</td>
                    <td className="text-center p-2">${session.totalCost.toFixed(3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}