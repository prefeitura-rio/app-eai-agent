'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';

export default function ChatPage() {
  return (
    <div className="grid md:grid-cols-[1fr_350px] gap-6 h-full">
      {/* Painel do Chat (Esquerda) */}
      <Card className="flex flex-col h-full">
        <CardHeader>
          <CardTitle>Chat</CardTitle>
        </CardHeader>
        <Separator />
        <CardContent className="flex-1 flex items-center justify-center text-muted-foreground">
          <p>Interface do chat em breve...</p>
        </CardContent>
      </Card>

      {/* Painel de Parâmetros (Direita) */}
      <Card className="h-full">
        <CardHeader>
          <CardTitle>Parâmetros</CardTitle>
        </CardHeader>
        <Separator />
        <CardContent className="flex items-center justify-center text-muted-foreground h-full">
          <p>Seleção de parâmetros em breve...</p>
        </CardContent>
      </Card>
    </div>
  );
}