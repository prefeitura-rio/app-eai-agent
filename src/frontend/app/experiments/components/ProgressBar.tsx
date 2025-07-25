'use client';

import React from 'react';
import styles from './ProgressBar.module.css';

interface ProgressBarProps {
  score: number;
  metricName: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ score, metricName }) => {
  const percentage = (score * 100).toFixed(0);
  let barClass = styles.metric_default;
  if (score >= 0.8) {
    barClass = styles.metric_high;
  } else if (score >= 0.5) {
    barClass = styles.metric_mid;
  } else {
    barClass = styles.metric_low;
  }

  return (
    <div>
      <div className="fw-bold mb-1">{score.toFixed(2)}</div>
      <div className={styles.progress_container}>
        <div
          className={`${styles.progress_bar} ${barClass}`}
          style={{ width: `${percentage}%` }}
          title={`${metricName}: ${score.toFixed(3)}`}
        ></div>
      </div>
    </div>
  );
};

export default ProgressBar;
