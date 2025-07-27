// src/frontend/app/components/JsonViewerModal.tsx
'use client';

import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

interface JsonViewerModalProps {
  data: unknown;
  children: React.ReactNode; // The trigger element
}

export default function JsonViewerModal({ data, children }: JsonViewerModalProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="sm:max-w-[60vw]">
        <DialogHeader>
          <DialogTitle>JSON Completo</DialogTitle>
          <DialogDescription>
            Visualização completa do objeto JSON.
          </DialogDescription>
        </DialogHeader>
        <div className="max-h-[60vh] overflow-y-auto rounded-md bg-gray-950 p-4">
          <pre className="text-sm text-gray-300">
            <code>{JSON.stringify(data, null, 2)}</code>
          </pre>
        </div>
      </DialogContent>
    </Dialog>
  );
}