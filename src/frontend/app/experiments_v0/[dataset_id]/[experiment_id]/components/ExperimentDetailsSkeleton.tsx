// src/frontend/app/experiments/[dataset_id]/[experiment_id]/components/ExperimentDetailsSkeleton.tsx
import React from 'react';
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardHeader, CardContent } from "@/components/ui/card";

export default function ExperimentDetailsSkeleton() {
    return (
        <div className="grid md:grid-cols-[350px_1fr] gap-4 p-4 h-[calc(100vh-135px)]">
            {/* Sidebar Skeleton */}
            <aside className="flex flex-col bg-card border rounded-lg p-4 space-y-4">
                <Skeleton className="h-[120px] w-full" />
                <Skeleton className="h-[40px] w-1/2" />
                <div className="space-y-2">
                    {[...Array(10)].map((_, i) => (
                        <Skeleton key={i} className="h-[50px] w-full" />
                    ))}
                </div>
            </aside>

            {/* Main Content Skeleton */}
            <main className="overflow-y-auto bg-card border rounded-lg p-6 space-y-6">
                {/* Metadata Card Skeleton */}
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

                {/* Summary Metrics Card Skeleton */}
                <Card>
                    <CardHeader>
                        <Skeleton className="h-8 w-1/2" />
                    </CardHeader>
                    <CardContent className="grid grid-cols-3 gap-4">
                        {[...Array(3)].map((_, i) => (
                            <Skeleton key={i} className="h-[120px] w-full" />
                        ))}
                    </CardContent>
                </Card>

                {/* Run Details Placeholder Skeleton */}
                <Card>
                    <CardContent className="pt-6">
                        <Skeleton className="h-[200px] w-full" />
                    </CardContent>
                </Card>
            </main>
        </div>
    );
}