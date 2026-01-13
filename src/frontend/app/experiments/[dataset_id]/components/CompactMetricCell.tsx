'use client';

import React from 'react';

interface CompactMetricCellProps {
  score: number | null | undefined;
}

function getBarColor(score: number): string {
  if (score >= 0.8) return 'bg-green-500';
  if (score >= 0.5) return 'bg-yellow-500';
  return 'bg-red-500';
}

export default function CompactMetricCell({ score }: CompactMetricCellProps) {
  const isValidScore = typeof score === 'number' && !isNaN(score);
  
  if (!isValidScore) {
    return (
      <div className="flex flex-col items-center justify-center h-full px-2 py-1">
        <span className="text-sm text-muted-foreground">—</span>
      </div>
    );
  }

  const barColor = getBarColor(score);
  const percentage = score * 100;

  return (
    <div className="flex flex-col items-center justify-center h-full px-2 py-1">
      <span className="text-sm font-semibold">
        {score.toFixed(2)}
      </span>
      <div className="w-14 h-1.5 bg-muted rounded-full mt-1 overflow-hidden">
        <div 
          className={`h-full rounded-full ${barColor}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
