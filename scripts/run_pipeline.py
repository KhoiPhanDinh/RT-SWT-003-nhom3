from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_step(script_name: str) -> None:
    script_path = Path(__file__).resolve().parent / script_name
    print("\n" + "=" * 80)
    print(f"Running: {script_path}")
    print("=" * 80)

    result = subprocess.run([sys.executable, str(script_path)], check=False)
    if result.returncode != 0:
        raise SystemExit(f"Step failed: {script_name}")


def main() -> int:
    run_step("validate_mutant_pool.py")
    run_step("run_gpt_ranking.py")
    run_step("random_baseline.py")

    print("\nPipeline completed.")
    print("Expected outputs:")
    print("- results/pilot_gpt_ranking.csv")
    print("- results/pilot_gpt_selected.csv")
    print("- results/pilot_random_selected.csv")
    print("- logs/pilot_api_log.txt")
    print("- logs/pilot_cost_log.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
