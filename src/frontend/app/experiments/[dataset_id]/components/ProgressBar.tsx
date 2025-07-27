'use client';

import React from 'react';
import { Progress } from "@/components/ui/progress";
import { cn } from '@/lib/utils';

interface ProgressBarProps {
  score: number;
  metricName: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ score, metricName }) => {
  const percentage = score * 100;

  const indicatorClass = cn({
    "bg-green-500": score >= 0.8,
    "bg-yellow-500": score >= 0.5 && score < 0.8,
    "bg-red-500": score < 0.5,
  });

  return (
    <div className="flex flex-col items-center gap-1">
      <span className="font-bold text-sm">{score.toFixed(2)}</span>
      <Progress 
        value={percentage} 
        className="w-24 h-2" 
        indicatorClassName={indicatorClass}
        title={`${metricName}: ${score.toFixed(3)}`}
      />
    </div>
  );
};

export default ProgressBar;