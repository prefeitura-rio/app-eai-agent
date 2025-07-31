// src/frontend/app/experiments/components/datasets-skeleton.tsx
import React from 'react';
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function DatasetsSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-end gap-4">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-10 w-10" />
        <Skeleton className="h-10 w-10" />
      </div>
      <div className="overflow-auto h-[calc(100vh-16rem)] border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[30%]"><Skeleton className="h-6 w-full" /></TableHead>
              <TableHead><Skeleton className="h-6 w-full" /></TableHead>
              <TableHead className="w-[120px]"><Skeleton className="h-6 w-full" /></TableHead>
              <TableHead className="w-[120px]"><Skeleton className="h-6 w-full" /></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {[...Array(5)].map((_, i) => (
              <TableRow key={i}>
                <TableCell><Skeleton className="h-5 w-full" /></TableCell>
                <TableCell><Skeleton className="h-5 w-full" /></TableCell>
                <TableCell><Skeleton className="h-5 w-full" /></TableCell>
                <TableCell><Skeleton className="h-5 w-full" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
