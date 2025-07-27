'use client';

import React from 'react';
import { Progress } from "@/components/ui/progress";
import { getScoreProgressClass } from '@/app/utils/utils';

interface ProgressBarProps {
  score: number;
  metricName: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ score, metricName }) => {
  // The score is now 0-10, so we multiply by 10 for the progress bar percentage
  const percentage = score * 100; 

  const indicatorClass = getScoreProgressClass(score);

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
