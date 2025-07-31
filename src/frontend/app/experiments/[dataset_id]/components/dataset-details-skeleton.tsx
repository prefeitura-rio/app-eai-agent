// src/frontend/app/experiments/[dataset_id]/components/dataset-details-skeleton.tsx
import React from 'react';
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function DatasetDetailsSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-10 w-64" />
        <div className="flex items-center gap-4">
            <Skeleton className="h-10 w-64" />
            <Skeleton className="h-10 w-10" />
            <Skeleton className="h-10 w-10" />
        </div>
      </div>
      <div className="overflow-auto h-[calc(100vh-16rem)] border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
                <TableCell><Skeleton className="h-6 w-full" /></TableCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {[...Array(10)].map((_, i) => (
              <TableRow key={i}>
                <TableCell><Skeleton className="h-5 w-full" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
