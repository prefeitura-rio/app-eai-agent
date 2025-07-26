// src/frontend/app/components/skeletons/ExperimentDetailsSkeleton.tsx
import React from 'react';
import styles from './Skeleton.module.css';

const SkeletonBlock = ({ height, width, className }: { height?: string, width?: string, className?: string }) => (
    <div className={`${styles.skeleton} ${className || ''}`} style={{ height, width }}></div>
);

export default function ExperimentDetailsSkeleton() {
    return (
        <div className={styles.twoColumnLayout}>
            {/* Sidebar Skeleton */}
            <aside className={styles.runListColumn}>
                <SkeletonBlock height="150px" className="mb-4" />
                <SkeletonBlock height="40px" className="mb-3" />
                <div className="list-group list-group-flush">
                    {[...Array(10)].map((_, i) => (
                        <SkeletonBlock key={i} height="50px" className="mb-2" />
                    ))}
                </div>
            </aside>

            {/* Main Content Skeleton */}
            <main className={styles.detailsColumn}>
                {/* Metadata Card Skeleton */}
                <div className={`${styles.skeletonCard} ${styles.skeleton}`}>
                    <SkeletonBlock height="2em" width="40%" className="mb-4" />
                    <div className="row">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="col-md-3 mb-3">
                                <SkeletonBlock height="1.5em" width="60%" className="mb-2" />
                                <SkeletonBlock height="1em" width="80%" />
                            </div>
                        ))}
                    </div>
                </div>

                {/* Summary Metrics Card Skeleton */}
                <div className={`${styles.skeletonCard} ${styles.skeleton}`}>
                    <SkeletonBlock height="2em" width="50%" className="mb-4" />
                    <div className="row">
                        {[...Array(3)].map((_, i) => (
                            <div key={i} className="col-md-4 mb-3">
                                <SkeletonBlock height="120px" />
                            </div>
                        ))}
                    </div>
                </div>

                {/* Run Details Placeholder Skeleton */}
                <div className={`${styles.skeletonCard} ${styles.skeleton}`}>
                    <SkeletonBlock height="200px" />
                </div>
            </main>
        </div>
    );
}
