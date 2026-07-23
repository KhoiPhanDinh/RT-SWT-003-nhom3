from pathlib import Path
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))

sample_path = ROOT / CONFIG["data"]["sample_path"]
gt_path = ROOT / CONFIG["data"]["ground_truth_path"]

required_sample = [
    "mutant_id", "project", "version", "class_name", "method_name",
    "line_number", "mutation_operator", "original_code",
    "mutated_code", "surrounding_context",
]

print("=" * 60)
print("CHECK FULL DATA")
print("=" * 60)

if not sample_path.exists():
    raise FileNotFoundError(f"Missing sample file: {sample_path}")

sample = pd.read_csv(sample_path)
print("sample_path:", sample_path)
print("sample shape:", sample.shape)

missing_cols = [c for c in required_sample if c not in sample.columns]
if missing_cols:
    raise ValueError(f"Missing sample columns: {missing_cols}")

print("\nProject counts:")
print(sample["project"].value_counts())

print("\nProject/version counts:")
print(sample.groupby(["project", "version"]).size())

print("\nDuplicate mutant_id:", int(sample["mutant_id"].duplicated().sum()))

print("\nEmpty required sample fields:")
for c in required_sample:
    empty = int(sample[c].isna().sum() + (sample[c].astype(str).str.strip() == "").sum())
    print(f"{c}: {empty}")

if gt_path.exists():
    gt = pd.read_csv(gt_path)
    print("\nground_truth_path:", gt_path)
    print("ground truth shape:", gt.shape)
    print("Duplicate ground_truth mutant_id:", int(gt["mutant_id"].duplicated().sum()))

    sample_ids = set(sample["mutant_id"].astype(str))
    gt_ids = set(gt["mutant_id"].astype(str))
    print("sample not in ground truth:", len(sample_ids - gt_ids))
    print("ground truth not in sample:", len(gt_ids - sample_ids))

    if "status" in gt.columns:
        print("\nStatus counts:")
        print(gt["status"].value_counts(dropna=False))

        # Per-project health check. A global status count hides a project whose
        # PIT run produced no coverage at all: Codec came back 2317/2317
        # NO_COVERAGE (test suite never executed, likely a source-layout
        # mismatch) and that was invisible in the global totals above.
        print("\nPer-project status health:")
        problems = []
        for proj, g in gt.groupby("project"):
            killed = int((g["status"].astype(str).str.upper() == "KILLED").sum())
            no_cov = int((g["status"].astype(str).str.upper() == "NO_COVERAGE").sum())
            n = len(g)
            flag = ""
            if killed == 0:
                flag = "  <-- FAIL: no killed mutants at all"
                problems.append(f"{proj}: 0/{n} killed")
            elif no_cov / n > 0.50:
                flag = "  <-- WARN: >50% NO_COVERAGE"
                problems.append(f"{proj}: {no_cov}/{n} NO_COVERAGE")
            print(f"  {proj:<14} killed={killed:>6}/{n:<6} ({killed/n:6.1%})"
                  f"  NO_COVERAGE={no_cov:>6} ({no_cov/n:5.1%}){flag}")

        if problems:
            print("\n" + "!" * 60)
            print("GROUND TRUTH LOOKS BROKEN FOR:")
            for p in problems:
                print(f"  - {p}")
            print("Do NOT compute metrics on these projects until PIT is re-run.")
            print("!" * 60)

    if "killed" in gt.columns:
        print("\nKilled counts:")
        print(gt["killed"].value_counts(dropna=False))
else:
    print("\nWARNING: full_ground_truth.csv is missing.")
    print("You can run LLM ranking with full_sample.csv, but metric computation needs full_ground_truth.csv.")

print("\nDATA CHECK DONE")
