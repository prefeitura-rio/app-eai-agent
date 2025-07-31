'use client';

import React from 'react';
import { Progress } from "@/components/ui/progress";
import { getScoreProgressClass } from '@/app/utils/utils';

interface ProgressBarProps {
  score: number | null | undefined;
  metricName: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ score, metricName }) => {
  const isValidScore = typeof score === 'number' && !isNaN(score);
  const displayScore = isValidScore ? score.toFixed(2) : '—';
  const percentage = isValidScore ? score * 100 : 0;
  const indicatorClass = isValidScore ? getScoreProgressClass(score) : 'bg-muted';

  return (
    <div className="flex flex-col items-center gap-1">
      <span className="font-bold text-sm">{displayScore}</span>
      <Progress 
        value={percentage} 
        className="w-24 h-2" 
        indicatorClassName={indicatorClass}
        title={isValidScore ? `${metricName}: ${score.toFixed(3)}` : `${metricName}: N/A`}
      />
    </div>
  );
};

export default ProgressBar;
