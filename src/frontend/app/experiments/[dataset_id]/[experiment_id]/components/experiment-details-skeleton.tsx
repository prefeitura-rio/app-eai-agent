// src/frontend/app/experiments/[dataset_id]/[experiment_id]/components/experiment-details-skeleton.tsx
import React from 'react';
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardHeader, CardContent } from "@/components/ui/card";

export default function ExperimentDetailsSkeleton() {
    return (
        <div className="grid md:grid-cols-[300px_1fr] gap-6 h-full pb-6">
            {/* Sidebar Skeleton */}
            <Card className="flex flex-col">
                <CardHeader>
                    <Skeleton className="h-8 w-3/4" />
                </CardHeader>
                <CardContent className="flex-1 overflow-y-auto space-y-2">
                    {[...Array(10)].map((_, i) => (
                        <Skeleton key={i} className="h-12 w-full" />
                    ))}
                </CardContent>
            </Card>

            {/* Main Content Skeleton */}
            <div className="overflow-y-auto space-y-6 pr-4">
                <Card>
                    <CardHeader>
                        <Skeleton className="h-8 w-1/3" />
                    </CardHeader>
                    <CardContent className="grid grid-cols-4 gap-4">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="space-y-2">
                                <Skeleton className="h-4 w-2/3" />
                                <Skeleton className="h-4 w-full" />
                            </div>
                        ))}
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="pt-6">
                        <Skeleton className="h-[200px] w-full" />
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
