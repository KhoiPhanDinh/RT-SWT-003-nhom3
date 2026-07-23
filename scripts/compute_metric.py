import math
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

try:
    from scipy.stats import wilcoxon
except Exception:
    wilcoxon = None


ROOT = Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))

GT_PATH = ROOT / CONFIG["data"]["ground_truth_path"]
RESULTS_DIR = ROOT / CONFIG["output"]["results_dir"]

GPT_SELECTED_PATH = RESULTS_DIR / "full_gpt_selected.csv"

SUMMARY_PATH = RESULTS_DIR / "full_selection_summary.csv"
PROJECT_VERSION_SCORES_PATH = RESULTS_DIR / "full_project_version_scores.csv"
PAIRED_PATH = RESULTS_DIR / "full_paired_mutation_scores.csv"
STATS_PATH = RESULTS_DIR / "full_statistical_summary.csv"


def normalize_bool(x):
    if isinstance(x, bool):
        return x
    s = str(x).strip().lower()
    return s in {"true", "1", "yes", "y", "killed"}


def load_ground_truth():
    if not GT_PATH.exists():
        raise FileNotFoundError(
            f"Missing ground truth file: {GT_PATH}\n"
            "Copy Kaggle output full_ground_truth.csv into data/ first."
        )

    gt = pd.read_csv(GT_PATH)
    gt["mutant_id"] = gt["mutant_id"].astype(str)

    if "killed" in gt.columns:
        gt["killed_bool"] = gt["killed"].apply(normalize_bool)
    elif "status" in gt.columns:
        gt["killed_bool"] = gt["status"].astype(str).str.upper().eq("KILLED")
    else:
        raise ValueError("Ground truth must contain either killed or status column.")

    if "status" not in gt.columns:
        gt["status"] = np.where(gt["killed_bool"], "KILLED", "NOT_KILLED")

    return gt


def score_selection(selection_path, method, seed=None):
    sel = pd.read_csv(selection_path)
    sel["mutant_id"] = sel["mutant_id"].astype(str)

    joined = sel.merge(
        GT[["mutant_id", "project", "version", "status", "killed_bool"]],
        on="mutant_id",
        how="left",
        suffixes=("", "_gt"),
    )

    if joined["killed_bool"].isna().any():
        missing = int(joined["killed_bool"].isna().sum())
        raise ValueError(f"{selection_path} has {missing} mutant_ids missing in ground truth.")

    total = len(joined)
    killed = int(joined["killed_bool"].sum())
    mutation_score = killed / total if total else math.nan

    status_counts = joined["status"].value_counts(dropna=False).to_dict()

    summary = {
        "method": method,
        "seed": seed if seed is not None else "",
        "selected": total,
        "killed": killed,
        "mutation_score": mutation_score,
    }

    for status, count in status_counts.items():
        summary[f"status_{status}"] = int(count)

    grouped = (
        joined
        .groupby(["project", "version"], dropna=False)
        .agg(
            selected=("mutant_id", "count"),
            killed=("killed_bool", "sum"),
        )
        .reset_index()
    )

    grouped["mutation_score"] = grouped["killed"] / grouped["selected"]
    grouped["method"] = method
    grouped["seed"] = seed if seed is not None else ""

    return summary, grouped


GT = load_ground_truth()

if not GPT_SELECTED_PATH.exists():
    raise FileNotFoundError(f"Missing GPT selected file: {GPT_SELECTED_PATH}. Run run_pipeline.py first.")

summary_rows = []
group_rows = []

s, g = score_selection(GPT_SELECTED_PATH, "GPT", None)
summary_rows.append(s)
group_rows.append(g)

random_paths = sorted(RESULTS_DIR.glob("full_random_selected_seed*.csv"))
if not random_paths:
    raise FileNotFoundError("No random selected files found. Run run_pipeline.py first.")

for path in random_paths:
    seed = path.stem.replace("full_random_selected_seed", "")
    s, g = score_selection(path, "RANDOM", seed)
    summary_rows.append(s)
    group_rows.append(g)

summary = pd.DataFrame(summary_rows)
groups = pd.concat(group_rows, ignore_index=True)

summary.to_csv(SUMMARY_PATH, index=False)
groups.to_csv(PROJECT_VERSION_SCORES_PATH, index=False)

# Paired group-level comparison by project-version for each random seed.
paired_rows = []
gpt_groups = groups[groups["method"] == "GPT"][["project", "version", "mutation_score", "selected", "killed"]].rename(
    columns={
        "mutation_score": "gpt_mutation_score",
        "selected": "gpt_selected",
        "killed": "gpt_killed",
    }
)

for seed in groups.loc[groups["method"] == "RANDOM", "seed"].unique():
    rand_groups = groups[(groups["method"] == "RANDOM") & (groups["seed"] == seed)][
        ["project", "version", "mutation_score", "selected", "killed"]
    ].rename(
        columns={
            "mutation_score": "random_mutation_score",
            "selected": "random_selected",
            "killed": "random_killed",
        }
    )

    pair = gpt_groups.merge(rand_groups, on=["project", "version"], how="outer")
    pair["seed"] = seed

    for col in ["gpt_mutation_score", "random_mutation_score"]:
        pair[col] = pair[col].fillna(0.0)
    for col in ["gpt_selected", "gpt_killed", "random_selected", "random_killed"]:
        pair[col] = pair[col].fillna(0).astype(int)

    pair["diff"] = pair["gpt_mutation_score"] - pair["random_mutation_score"]
    paired_rows.append(pair)

paired = pd.concat(paired_rows, ignore_index=True)
paired.to_csv(PAIRED_PATH, index=False)

stats_rows = []

# Overall simple comparison against each random seed
gpt_overall = summary[summary["method"] == "GPT"].iloc[0]
for _, rand in summary[summary["method"] == "RANDOM"].iterrows():
    stats_rows.append({
        "comparison": f"GPT_vs_RANDOM_seed{rand['seed']}_overall",
        "gpt_mutation_score": float(gpt_overall["mutation_score"]),
        "random_mutation_score": float(rand["mutation_score"]),
        "diff": float(gpt_overall["mutation_score"] - rand["mutation_score"]),
        "n_pairs": "",
        "wilcoxon_p_value": "",
        "note": "overall selected-set comparison",
    })

# Group-level Wilcoxon
for seed in paired["seed"].unique():
    sub = paired[paired["seed"] == seed].copy()
    diffs = sub["diff"].astype(float).values
    nonzero = diffs[np.abs(diffs) > 1e-12]

    p_value = ""
    note = ""
    if wilcoxon is None:
        note = "scipy unavailable"
    elif len(nonzero) < 2:
        note = "not enough nonzero pairs for Wilcoxon"
    else:
        try:
            _, p_value = wilcoxon(nonzero, alternative="greater")
            p_value = float(p_value)
            note = "one-sided Wilcoxon on project-version mutation-score differences"
        except Exception as e:
            note = f"Wilcoxon failed: {e}"

    stats_rows.append({
        "comparison": f"GPT_vs_RANDOM_seed{seed}_project_version",
        "gpt_mutation_score": "",
        "random_mutation_score": "",
        "diff": float(np.mean(diffs)) if len(diffs) else "",
        "n_pairs": int(len(diffs)),
        "wilcoxon_p_value": p_value,
        "note": note,
    })

stats = pd.DataFrame(stats_rows)
stats.to_csv(STATS_PATH, index=False)

print("=" * 60)
print("FULL METRIC SUMMARY")
print("=" * 60)

print("\nSelection summary:")
print(summary)

print("\nStatistical summary:")
print(stats)

print("\nSaved:")
print(SUMMARY_PATH)
print(PROJECT_VERSION_SCORES_PATH)
print(PAIRED_PATH)
print(STATS_PATH)
