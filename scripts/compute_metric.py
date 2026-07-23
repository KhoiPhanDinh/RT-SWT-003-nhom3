"""RBL-4 §8.3 - Tuần 8 statistical analysis (MS role).

Computes mutation score (MS = Killed / Selected) per (project, version,
class_name) group for both selection strategies (GPT4o-mini vs random
fixed-seed), pairs the groups, and runs the pre-registered statistical test
from team-synthesis/proposal.md §5.6 / §6.1:

    Wilcoxon signed-rank test, one-sided (alternative="greater", H1: MS_GPT4o > MS_random)
    Effect size: matched-pairs rank-biserial correlation (r_rb)

Sub-group analysis (proposal §6.3, pre-registered): Commons Lang vs Commons
Math, only run the test per sub-group if n_group >= 10, else descriptive only.

Output: results/summary.csv (one row per analysis: metric, p_value,
effect_size, N, plus descriptive stats).

Usage:
    python scripts/compute_metric.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from utils import load_config, resolve_path

GROUP_COLS = ["project", "version", "class_name"]
N_GROUP_MIN = 10  # pre-registered threshold, proposal §6.3


def to_bool_killed(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin(["true", "1", "yes"])


def load_selected_with_killed(path: Path, ground_truth: pd.DataFrame) -> pd.DataFrame:
    selected = pd.read_csv(path)
    selected["mutant_id"] = selected["mutant_id"].astype(str)
    merged = selected.merge(
        ground_truth[["mutant_id", "killed"]], on="mutant_id", how="left"
    )
    missing = int(merged["killed"].isna().sum())
    if missing:
        raise ValueError(
            f"{path}: {missing} selected mutant_id not found in full_ground_truth.csv "
            "(selection and ground truth are out of sync)."
        )
    return merged


def group_mutation_score(df: pd.DataFrame, label: str) -> pd.DataFrame:
    g = df.groupby(GROUP_COLS, dropna=False).agg(
        selected=("mutant_id", "count"),
        killed=("killed", "sum"),
    )
    g["mutation_score"] = g["killed"] / g["selected"]
    g = g.rename(columns={"selected": f"selected_{label}", "killed": f"killed_{label}", "mutation_score": f"ms_{label}"})
    return g


def rank_biserial_from_wilcoxon(diff: np.ndarray) -> float:
    """Matched-pairs rank-biserial correlation, r_rb = (W+ - W-) / (n(n+1)/2).

    diff: nonzero paired differences (zeros already dropped, matching what
    scipy.stats.wilcoxon does internally with zero_method='wilcox').
    """
    nz = diff[diff != 0]
    n = len(nz)
    if n == 0:
        return float("nan")
    ranks = pd.Series(np.abs(nz)).rank(method="average").to_numpy()
    w_pos = ranks[nz > 0].sum()
    w_neg = ranks[nz < 0].sum()
    total = n * (n + 1) / 2
    return (w_pos - w_neg) / total


def run_wilcoxon_one_sided_greater(paired: pd.DataFrame, ms_gpt_col: str, ms_random_col: str) -> dict:
    diff = (paired[ms_gpt_col] - paired[ms_random_col]).to_numpy()
    n_pairs = len(diff)
    n_nonzero = int((diff != 0).sum())

    result = {
        "n_pairs": n_pairs,
        "n_nonzero_pairs": n_nonzero,
        "mean_ms_gpt": float(np.mean(paired[ms_gpt_col])) if n_pairs else float("nan"),
        "mean_ms_random": float(np.mean(paired[ms_random_col])) if n_pairs else float("nan"),
        "median_ms_gpt": float(np.median(paired[ms_gpt_col])) if n_pairs else float("nan"),
        "median_ms_random": float(np.median(paired[ms_random_col])) if n_pairs else float("nan"),
        "win_gpt": int((diff > 0).sum()),
        "win_random": int((diff < 0).sum()),
        "tie": int((diff == 0).sum()),
        "p_value": float("nan"),
        "effect_size_rank_biserial": float("nan"),
        "test_run": False,
    }

    if n_nonzero == 0:
        result["note"] = "All paired differences are zero (or no pairs); Wilcoxon not run."
        return result

    stat, p_value = wilcoxon(diff, alternative="greater", zero_method="wilcox")
    result["p_value"] = float(p_value)
    result["effect_size_rank_biserial"] = rank_biserial_from_wilcoxon(diff)
    result["test_run"] = True
    return result


def build_paired_table(gpt: pd.DataFrame, random_: pd.DataFrame) -> pd.DataFrame:
    ms_gpt = group_mutation_score(gpt, "gpt")
    ms_random = group_mutation_score(random_, "random")
    paired = ms_gpt.join(ms_random, how="inner").reset_index()
    return paired


def analyze_subset(paired: pd.DataFrame, label: str) -> dict:
    row = run_wilcoxon_one_sided_greater(paired, "ms_gpt", "ms_random")
    row["subset"] = label
    row["n_group"] = len(paired)
    row["ran_test"] = row["test_run"] and row["n_group"] >= N_GROUP_MIN
    if not row["ran_test"]:
        row["reason_skipped"] = (
            "n_group < 10 (pre-registered threshold, proposal §6.3): descriptive only"
            if row["n_group"] < N_GROUP_MIN
            else row.get("note", "")
        )
    return row


def main() -> int:
    cfg = load_config()
    ground_truth_path = resolve_path("data/full_ground_truth.csv")
    gpt_selected_path = resolve_path("results/full_gpt_selected.csv")
    random_selected_path = resolve_path("results/full_random_selected.csv")
    summary_path = resolve_path("results/summary.csv")
    paired_out_path = resolve_path("results/paired_mutation_scores.csv")

    ground_truth = pd.read_csv(ground_truth_path)
    ground_truth["mutant_id"] = ground_truth["mutant_id"].astype(str)
    ground_truth["killed"] = to_bool_killed(ground_truth["killed"])

    gpt = load_selected_with_killed(gpt_selected_path, ground_truth)
    random_ = load_selected_with_killed(random_selected_path, ground_truth)
    gpt["killed"] = to_bool_killed(gpt["killed"])
    random_["killed"] = to_bool_killed(random_["killed"])

    paired_all = build_paired_table(gpt, random_)
    paired_all.to_csv(paired_out_path, index=False, encoding="utf-8")

    rows = []
    rows.append(analyze_subset(paired_all, "RQ1_pooled_all_projects"))

    for project in sorted(paired_all["project"].unique()):
        subset = paired_all[paired_all["project"] == project]
        rows.append(analyze_subset(subset, f"RQ1_subgroup_{project}"))

    summary = pd.DataFrame(rows)
    ordered_cols = [
        "subset", "n_group", "n_pairs", "n_nonzero_pairs",
        "mean_ms_gpt", "mean_ms_random", "median_ms_gpt", "median_ms_random",
        "win_gpt", "win_random", "tie",
        "p_value", "effect_size_rank_biserial", "ran_test", "reason_skipped",
    ]
    for c in ordered_cols:
        if c not in summary.columns:
            summary[c] = np.nan
    summary = summary[ordered_cols]
    summary.to_csv(summary_path, index=False, encoding="utf-8")

    print(f"Saved paired mutation scores: {paired_out_path} ({len(paired_all)} groups)")
    print(f"Saved summary: {summary_path}")
    print()
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
