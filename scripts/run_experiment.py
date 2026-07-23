"""Tuần 8 full-experiment orchestrator (RBL-4 §8.2).

Runs the complete corrected pipeline in order:
  1. validate_mutant_pool.py  - sanity-check data/full_sample.csv
  2. run_gpt_ranking.py       - GPT4o-mini ranking over the whole pool (resumable)
  3. random_baseline.py       - fixed-seed random baseline, same budget
  4. reselect_by_group.py     - apply selection_scope=by_group (project+version+class_name)
                                 to both GPT and random output, so every group gets its
                                 proportional share (fixes the global-scope bug where Math
                                 got 0 selected mutants - see notes.md).

Equivalent to LR_v2/LR/scripts/run_pipeline.py, renamed/extended to match the
RBL-4 required script name and to include the by-group reselection step.
"""
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
    run_step("reselect_by_group.py")

    print("\nFull experiment pipeline completed.")
    print("Expected outputs:")
    print("- results/full_llm_output.csv")
    print("- results/full_gpt_selected.csv   (by_group, corrected)")
    print("- results/full_random_selected.csv (by_group, corrected)")
    print("- results/full_api_log.txt")
    print("- results/full_cost_log.csv")
    print("Next step: python scripts/compute_metric.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
