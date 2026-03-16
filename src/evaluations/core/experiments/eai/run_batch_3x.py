import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


RUNS_PER_SCRIPT = int(os.getenv("EAI_BATCH_RUNS_PER_SCRIPT", "3"))
SLEEP_BETWEEN_RUNS_SECONDS = float(os.getenv("EAI_BATCH_SLEEP_SECONDS", "1"))
SCRIPT_ORDER = [
    "run_equipments.py",
    "run_memory_experiment.py",
    "run_disaster_eval.py",
    "run_servicos.py",
]


def run_script(
    script_path: Path,
    run_number: int,
    total_runs: int,
    reasoning_engine_id: str | None,
) -> None:
    print(f"[{run_number}/{total_runs}] Executando {script_path.name}...")
    cmd = [sys.executable, str(script_path)]
    if reasoning_engine_id:
        cmd.extend(["--reasoning-engine-id", reasoning_engine_id])
    subprocess.run(cmd, check=True)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run batch experiments (3x each).")
    parser.add_argument(
        "--reasoning-engine-id",
        dest="reasoning_engine_id",
        default=None,
        help="ID do reasoning engine a ser usado (opcional).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    base_dir = Path(__file__).resolve().parent
    total_runs = len(SCRIPT_ORDER) * RUNS_PER_SCRIPT
    current_run = 1

    for script_name in SCRIPT_ORDER:
        script_path = base_dir / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {script_path}")

        for _ in range(RUNS_PER_SCRIPT):
            run_script(script_path, current_run, total_runs, args.reasoning_engine_id)
            if current_run < total_runs:
                print(
                    f"Aguardando {SLEEP_BETWEEN_RUNS_SECONDS}s antes da próxima execução..."
                )
                time.sleep(SLEEP_BETWEEN_RUNS_SECONDS)
            current_run += 1

    print("Concluído: 3x run_equipments, 3x run_memory_experiment, 3x run_servicos.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Falha ao executar {exc.cmd}: código de saída {exc.returncode}")
        raise SystemExit(exc.returncode)
