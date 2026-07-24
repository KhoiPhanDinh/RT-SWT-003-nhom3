"""ROLE MS (Phan tich thong ke) — §8.3 RBL-4, ap cho SWT_EX.

Sinh dung bo file MS ma RBL-4 (RT-SWT-003-nhom3) co, cung schema:
  1. full_overall_mutation_score.csv
  2. full_project_summary.csv
  3. full_coverage_by_project.csv
  4. paired_mutation_scores.csv
  5. summary.csv   (metric, p-value, effect size, N, ket luan per RQ)

Theo §8.3:
  - Tinh metric tren toan bo output
  - Chay statistical test da chon trong proposal (Wilcoxon signed-rank, 1 phia, α=0.05)
  - Tinh effect size (rank-biserial; nho<0.2, trung binh 0.2-0.5, lon>0.5)
  - Ket luan tung RQ: reject H0 / fail to reject H0
  - KHONG doi test sau khi xem data (HARKing).

Cau hinh:
  - Random baseline = seed42 (seed nhom da chay; RT cung dung 1 nhanh random).
  - Selection = by_group (da sua budget lech + Codec da fix). Xem amendment_v1.2.
  - §6.3: n_group < 10 -> chi descriptive, khong chay test.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
KEYS = ["project", "version", "class_name"]
ALPHA = 0.05
PRIMARY_SEED = 42
MIN_GROUP_FOR_TEST = 10  # §6.3

GPT_SEL = RESULTS / "full_gpt_selected_bygroup.csv"
RND_SEL = RESULTS / f"full_random_selected_bygroup_seed{PRIMARY_SEED}.csv"
LLM_OUT = RESULTS / "full_llm_output.csv"


def load_killmap() -> dict:
    gt = pd.read_csv(DATA / "full_ground_truth.csv")
    gt["mutant_id"] = gt["mutant_id"].astype(str)
    k = gt["status"].astype(str).str.upper().eq("KILLED").astype(int)
    return dict(zip(gt["mutant_id"], k)), gt


def group_scores(path: Path, killmap: dict) -> pd.DataFrame:
    d = pd.read_csv(path)
    d["mutant_id"] = d["mutant_id"].astype(str)
    d["killed"] = d["mutant_id"].map(killmap)
    g = d.groupby(KEYS, dropna=False).agg(
        selected=("mutant_id", "count"), killed=("killed", "sum")).reset_index()
    g["ms"] = g["killed"] / g["selected"]
    return g, int(d["killed"].sum()), len(d)


def rank_biserial(nonzero: np.ndarray) -> float:
    ranks = pd.Series(np.abs(nonzero)).rank().values
    r_pos, r_neg = ranks[nonzero > 0].sum(), ranks[nonzero < 0].sum()
    return (r_pos - r_neg) / (r_pos + r_neg)


def wilcoxon_row(subset: str, paired: pd.DataFrame) -> dict:
    n_group = len(paired)
    diff = paired["diff_gpt_minus_random"].values
    nz = diff[np.abs(diff) > 1e-12]
    row = {
        "subset": subset,
        "n_group": n_group,
        "n_pairs": n_group,
        "n_nonzero_pairs": int(len(nz)),
        "mean_ms_gpt": paired["ms_gpt"].mean(),
        "mean_ms_random": paired["ms_random"].mean(),
        "median_ms_gpt": paired["ms_gpt"].median(),
        "median_ms_random": paired["ms_random"].median(),
        "win_gpt": int((diff > 1e-12).sum()),
        "win_random": int((diff < -1e-12).sum()),
        "tie": int((np.abs(diff) <= 1e-12).sum()),
        "p_value": "",
        "effect_size_rank_biserial": "",
        "ran_test": False,
        "reason_skipped": "",
    }
    if n_group < MIN_GROUP_FOR_TEST:
        row["reason_skipped"] = f"n_group < {MIN_GROUP_FOR_TEST} (§6.3): chi descriptive"
    elif len(nz) < 2:
        row["reason_skipped"] = "n_nonzero_pairs < 2: khong du cap de test"
    else:
        _, p = wilcoxon(nz, alternative="greater")   # 1 phia, dung proposal §6.1
        row["p_value"] = float(p)
        row["effect_size_rank_biserial"] = rank_biserial(nz)
        row["ran_test"] = True
    return row


def main() -> int:
    killmap, gt = load_killmap()
    gpt_g, gpt_sel_tot, _ = group_scores(GPT_SEL, killmap)
    rnd_g, rnd_sel_tot, _ = group_scores(RND_SEL, killmap)

    gk = int(gpt_g["killed"].sum()); gn = int(gpt_g["selected"].sum())
    rk = int(rnd_g["killed"].sum()); rn = int(rnd_g["selected"].sum())

    # ---- 1. full_overall_mutation_score.csv --------------------------------
    overall = pd.DataFrame([
        {"strategy": "GPT4o-mini", "selected": gn, "killed": gk, "mutation_score": gk / gn},
        {"strategy": "Random fixed-seed", "selected": rn, "killed": rk, "mutation_score": rk / rn},
    ])
    overall.to_csv(RESULTS / "full_overall_mutation_score.csv", index=False)

    # ---- 4. paired_mutation_scores.csv (can truoc de tinh summary) ----------
    paired = gpt_g.rename(columns={"selected": "selected_gpt", "killed": "killed_gpt", "ms": "ms_gpt"}).merge(
        rnd_g.rename(columns={"selected": "selected_random", "killed": "killed_random", "ms": "ms_random"}),
        on=KEYS, how="outer")
    for c in ["ms_gpt", "ms_random"]:
        paired[c] = paired[c].fillna(0.0)
    for c in ["selected_gpt", "killed_gpt", "selected_random", "killed_random"]:
        paired[c] = paired[c].fillna(0).astype(int)
    paired["diff_gpt_minus_random"] = paired["ms_gpt"] - paired["ms_random"]
    paired = paired.sort_values(KEYS).reset_index(drop=True)
    paired.to_csv(RESULTS / "paired_mutation_scores.csv", index=False)

    # ---- 2. full_project_summary.csv ---------------------------------------
    proj = paired.groupby("project").agg(
        n_group=("class_name", "count"),
        mean_ms_gpt=("ms_gpt", "mean"),
        mean_ms_random=("ms_random", "mean")).reset_index()
    proj["mean_diff"] = proj["mean_ms_gpt"] - proj["mean_ms_random"]
    proj.to_csv(RESULTS / "full_project_summary.csv", index=False)

    # ---- 3. full_coverage_by_project.csv -----------------------------------
    pool = gt.groupby("project").size().rename("ground_truth_pool")
    llm = pd.read_csv(LLM_OUT).groupby("project").size().rename("llm_output_pool") \
        if LLM_OUT.exists() else pool.rename("llm_output_pool")
    gsel = pd.read_csv(GPT_SEL).groupby("project").size().rename("gpt_selected")
    rsel = pd.read_csv(RND_SEL).groupby("project").size().rename("random_selected")
    cov = pd.concat([pool, llm, gsel, rsel], axis=1).reset_index()
    cov["gpt_selected_pct_of_pool"] = cov["gpt_selected"] / cov["ground_truth_pool"] * 100
    cov["random_selected_pct_of_pool"] = cov["random_selected"] / cov["ground_truth_pool"] * 100
    cov.to_csv(RESULTS / "full_coverage_by_project.csv", index=False)

    # ---- 5. summary.csv (RQ1 pooled + subgroup per project) -----------------
    rows = [wilcoxon_row("RQ1_pooled_all_projects", paired)]
    for p in sorted(paired["project"].unique()):
        rows.append(wilcoxon_row(f"RQ1_subgroup_{p}", paired[paired["project"] == p]))
    summary = pd.DataFrame(rows)
    summary.to_csv(RESULTS / "summary.csv", index=False)

    # ---- In ket luan (role MS: reject / fail to reject H0) ------------------
    print("=" * 74)
    print("ROLE MS — PHAN TICH THONG KE (SWT_EX) | random=seed42 | by_group | α=0.05")
    print("=" * 74)
    print(f"\nOverall MS: GPT4o-mini={gk/gn:.4f} ({gk}/{gn})  vs  Random={rk/rn:.4f} ({rk}/{rn})")
    print("\nKet luan per RQ (Wilcoxon 1 phia, effect size rank-biserial):")
    for _, r in summary.iterrows():
        if not r["ran_test"]:
            print(f"  {r['subset']:<28} n={r['n_group']:<3} SKIP: {r['reason_skipped']}")
            continue
        p = r["p_value"]; es = r["effect_size_rank_biserial"]
        mag = "lon" if abs(es) > 0.5 else "trung binh" if abs(es) >= 0.2 else "nho"
        # H1 SWT_EX pre-register goc: p<.05 & r_rb>=.30 & median(diff)>0
        med_diff = r["median_ms_gpt"] - r["median_ms_random"]
        h1 = (p < ALPHA and es >= 0.30 and med_diff > 0)
        verdict = "REJECT H0 (ung ho H1)" if h1 else "FAIL TO REJECT H0"
        print(f"  {r['subset']:<28} n={r['n_group']:<3} p={p:.4g}  r_rb={es:+.3f} ({mag})  "
              f"W/L/T={r['win_gpt']}/{r['win_random']}/{r['tie']}  -> {verdict}")

    print("\nDa ghi 5 file MS vao results/ (dung schema RBL-4):")
    for f in ["full_overall_mutation_score.csv", "full_project_summary.csv",
              "full_coverage_by_project.csv", "paired_mutation_scores.csv", "summary.csv"]:
        print(f"  results/{f}")
    print("\nLuu y: ket luan pre-register (group-weighted) FAIL TO REJECT do ties/median=0.")
    print("Xem compute_h1.py cho robustness (mutant-weighted p=0.0097, Monte Carlo p=0.0002)")
    print("va amendment_v1.2.md cho ket luan 'partial support'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
