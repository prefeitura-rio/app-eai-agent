# -*- coding: utf-8 -*-
import statistics
from collections import defaultdict, Counter
from typing import List, Dict, Any, TypedDict


class MetricStats(TypedDict):
    """Estrutura para armazenar estatísticas de métricas."""

    scores: List[float]
    times: List[float]
    errors: int


class ResultAnalyzer:
    """
    Calcula estatísticas e sumários agregados a partir dos resultados
    brutos de todas as execuções do experimento.
    """

    def analyze(
        self, runs: List[Dict[str, Any]], total_duration: float
    ) -> Dict[str, Any]:
        """
        Gera o relatório de análise completo.

        Args:
            runs: Lista de resultados de cada tarefa.
            total_duration: Duração total do experimento.

        Returns:
            Um dicionário contendo os sumários de métricas, erros e execução.
        """
        aggregate_metrics = self._calculate_metrics_summary(runs)
        error_summary = self._calculate_error_summary(runs)
        execution_summary = self._calculate_execution_summary(
            runs, total_duration, aggregate_metrics
        )

        return {
            "execution_summary": execution_summary,
            "error_summary": error_summary,
            "aggregate_metrics": aggregate_metrics,
        }

    def _safe_statistics(self, values: List[float]) -> Dict[str, float]:
        """Calcula estatísticas de forma segura."""
        if not values:
            return {}

        stats = {
            "average": round(statistics.mean(values), 4),
            "median": round(statistics.median(values), 4),
            "min": min(values),
            "max": max(values),
        }

        if len(values) > 1:
            stats["std_dev"] = round(statistics.stdev(values), 4)
        else:
            stats["std_dev"] = 0.0

        return stats

    def _calculate_metrics_summary(
        self, runs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calcula resumo das métricas com melhor tratamento de erros."""
        stats_by_metric: defaultdict[str, MetricStats] = defaultdict(
            lambda: {"scores": [], "times": [], "errors": 0}
        )

        for run in runs:
            if "error" in run:
                continue

            all_evaluations = []
            for analysis_key in ["one_turn_analysis", "multi_turn_analysis"]:
                analysis = run.get(analysis_key)
                if analysis and "evaluations" in analysis:
                    all_evaluations.extend(analysis["evaluations"])

            for evaluation in all_evaluations:
                metric_name = evaluation.get("metric_name", "unknown")
                stats = stats_by_metric[metric_name]
                stats["times"].append(evaluation.get("duration_seconds", 0.0))

                if evaluation.get("has_error") or evaluation.get("score") is None:
                    stats["errors"] += 1
                else:
                    score = evaluation.get("score")
                    if isinstance(score, (int, float)):
                        stats["scores"].append(float(score))

        metrics_summary = []
        for metric_name, stats in stats_by_metric.items():
            scores, times, error_count = (
                stats["scores"],
                stats["times"],
                stats["errors"],
            )
            successful_runs = len(scores)
            total_runs = successful_runs + error_count

            if total_runs == 0:
                continue

            score_distribution = []
            if successful_runs > 0:
                score_counts = Counter(scores)
                for score_value, count in sorted(score_counts.items()):
                    score_distribution.append(
                        {
                            "value": score_value,
                            "count": count,
                            "percentage": round((count / successful_runs) * 100, 2),
                        }
                    )

            summary = {
                "metric_name": metric_name,
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "success_rate_percentage": round(
                    (successful_runs / total_runs) * 100, 2
                ),
                "failed_runs": error_count,
                "failure_rate_percentage": round((error_count / total_runs) * 100, 2),
                "score_statistics": self._safe_statistics(scores) if scores else None,
                "duration_statistics_seconds": (
                    self._safe_statistics(times) if times else None
                ),
                "score_distribution": score_distribution,
            }
            metrics_summary.append(summary)

        return sorted(metrics_summary, key=lambda x: x["metric_name"])

    def _calculate_error_summary(self, runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula resumo de erros de forma mais eficiente."""
        error_breakdown = defaultdict(int)
        failed_run_ids = set()

        for run in runs:
            run_id = run.get("task_data", {}).get("id", "unknown")
            if "error" in run:
                failed_run_ids.add(run_id)
                continue

            has_evaluation_error = False
            for analysis_key in ["one_turn_analysis", "multi_turn_analysis"]:
                analysis = run.get(analysis_key)
                if analysis and "evaluations" in analysis:
                    for evaluation in analysis["evaluations"]:
                        if evaluation.get("has_error"):
                            has_evaluation_error = True
                            error_breakdown[evaluation.get("metric_name", "unknown")] += 1
            if has_evaluation_error:
                failed_run_ids.add(run_id)

        return {
            "total_failed_runs": len(failed_run_ids),
            "errors_per_metric": dict(sorted(error_breakdown.items())),
            "failed_run_ids": sorted(list(failed_run_ids)),
        }

    def _calculate_execution_summary(
        self,
        runs: List[Dict[str, Any]],
        total_duration: float,
        aggregate_metrics: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """Calcula resumo da execução."""
        task_durations = [
            r.get("duration_seconds", 0) for r in runs if "error" not in r
        ]
        avg_task_duration = (
            round(sum(task_durations) / len(task_durations), 2)
            if task_durations
            else 0.0
        )

        metric_durations = [
            m.get("duration_statistics_seconds", {}).get("average", 0)
            for m in aggregate_metrics
            if m.get("duration_statistics_seconds")
        ]
        avg_metric_duration = (
            round(sum(metric_durations) / len(metric_durations), 2)
            if metric_durations
            else 0.0
        )

        return {
            "total_duration_seconds": round(total_duration, 2),
            "average_task_duration_seconds": avg_task_duration,
            "average_metric_duration_seconds": avg_metric_duration,
        }
