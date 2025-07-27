import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Returns the Tailwind CSS class for a score badge based on the score value.
 * The score is expected to be between 0 and 1.
 * @param score The score value.
 * @returns The Tailwind CSS class string.
 */
export const getScoreBadgeClass = (score: number) => {
  if (score >= 0.8) {
    return 'bg-success hover:bg-success/90 text-success-foreground';
  } else if (score >= 0.5) {
    return 'bg-warning hover:bg-warning/90 text-warning-foreground';
  } else {
    return 'bg-destructive hover:bg-destructive/90 text-destructive-foreground';
  }
};

/**
 * Returns the Tailwind CSS class for a progress bar based on the score value.
 * The score is expected to be between 0 and 10.
 * @param score The score value.
 * @returns The Tailwind CSS class string.
 */
export const getScoreProgressClass = (score: number) => {
  if (score >= 0.8) {
    return 'bg-success';
  } else if (score >= 0.5) {
    return 'bg-warning';
  } else {
    return 'bg-destructive';
  }
};
