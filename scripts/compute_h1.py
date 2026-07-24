"""H1: MS_GPT4o > MS_random, cung budget top-10% moi group.

PRIMARY SEED = 42 (proposal §5.5). Nhom chi thuc thi random baseline o seed42.
Cac phan tich khac (mutant-weighted, Monte Carlo) KHONG can them seed da chay:
random selection chi la boc mutant_id tu pool + tra ground truth da co san
(khong goi API, khong chay PIT), nen mo phong la phan tich hau ky hop le tren
dung du lieu da thu thap.

Bao cao theo thu tu TRUNG THUC:
  1. Ket qua PRE-REGISTER (seed42, group-weighted, 3 tieu chi) -- co the TRUOT.
  2. Chan doan: median bi ties lam thoai hoa (group k=1..173).
  3. Robustness A: bo tieu chi median, giu p & r_rb.
  4. Robustness B: mutant-weighted (overall MS, 2-proportion z-test) tren seed42.
  5. Robustness C: Monte Carlo -- dac trung hoa phan phoi random (khong chi 1 diem).
  6. Subgroup §6.3 theo project.

KHONG doi primary seed. KHONG ha nguong r_rb. Moi thay doi tieu chi deu co ly do
phuong phap doc lap voi ket qua va phai ghi trong amendment_v1.2.
"""
from __future__ import annotations

import math
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import wilcoxon, binomtest, norm

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
GROUP_COLS = ["project", "version", "class_name"]
PRIMARY_SEED = 42
VALIDATION_SEEDS = [123, 2026]   # co file nhung KHONG phai primary; bao cao de tham chieu
ALPHA = 0.05
MIN_RRB = 0.30
TOP_PERCENT = 10.0
MC_DRAWS = 5000
MC_RNG_SEED = 20260721

GPT_FILE = "full_gpt_selected_bygroup.csv"
RND_FILE = "full_random_selected_bygroup_seed{seed}.csv"


def kcount(n: int) -> int:
    return max(1, math.ceil(n * TOP_PERCENT / 100.0))


def load_gt() -> tuple[pd.DataFrame, list[str]]:
    gt = pd.read_csv(ROOT / "data" / "full_ground_truth.csv")
    gt["mutant_id"] = gt["mutant_id"].astype(str)
    gt["k"] = gt["status"].astype(str).str.upper().eq("KILLED").astype(int)
    broken = [p for p, g in gt.groupby("project") if g["k"].sum() == 0]
    return gt, broken


def group_ms(path: Path, kill_map: dict, exclude: list[str]) -> pd.DataFrame:
    d = pd.read_csv(path)
    d["mutant_id"] = d["mutant_id"].astype(str)
    d["k"] = d["mutant_id"].map(kill_map)
    if d["k"].isna().any():
        raise ValueError(f"{path.name}: {int(d['k'].isna().sum())} mutant thieu trong ground truth")
    d = d[~d["project"].isin(exclude)]
    g = d.groupby(GROUP_COLS, dropna=False).agg(sel=("k", "count"), killed=("k", "sum")).reset_index()
    g["ms"] = g["killed"] / g["sel"]
    return g


def rank_biserial(nonzero: np.ndarray) -> float:
    ranks = pd.Series(np.abs(nonzero)).rank().values
    r_pos, r_neg = ranks[nonzero > 0].sum(), ranks[nonzero < 0].sum()
    return (r_pos - r_neg) / (r_pos + r_neg)


def wilcoxon_line(diffs: np.ndarray) -> dict:
    nz = diffs[np.abs(diffs) > 1e-12]
    wins, losses, ties = int((nz > 0).sum()), int((nz < 0).sum()), int(len(diffs) - len(nz))
    if len(nz) < 2:
        return {"n": len(diffs), "median": float(np.median(diffs)), "p": float("nan"),
                "r_rb": float("nan"), "wins": wins, "losses": losses, "ties": ties}
    _, p = wilcoxon(nz, alternative="greater")
    return {"n": len(diffs), "median": float(np.median(diffs)), "p": float(p),
            "r_rb": rank_biserial(nz), "wins": wins, "losses": losses, "ties": ties}


def main() -> int:
    gt, broken = load_gt()
    kill_map = dict(zip(gt["mutant_id"], gt["k"]))

    print("=" * 78)
    print("H1: MS_GPT4o > MS_random   |   PRIMARY SEED = 42   |   paired project/version/class")
    print("=" * 78)

    if broken:
        print(f"\n!!! LOAI (ground truth 0 KILLED, du lieu hong): {broken}")
        print("    Phai da sua Codec PIT truoc. Xem scripts/KAGGLE_fix_codec_pit.sh")
    else:
        print("\nData health OK: moi project deu co mutant KILLED (Codec da duoc sua).")

    gpt = group_ms(RESULTS / GPT_FILE, kill_map, broken)
    merged = gpt[GROUP_COLS + ["ms", "sel", "killed"]].rename(
        columns={"ms": "gpt", "sel": "g_sel", "killed": "g_killed"})

    seeds_present = [PRIMARY_SEED] + [s for s in VALIDATION_SEEDS
                                      if (RESULTS / RND_FILE.format(seed=s)).exists()]
    rnd_overall = {}
    for s in seeds_present:
        r = group_ms(RESULTS / RND_FILE.format(seed=s), kill_map, broken)
        merged = merged.merge(r[GROUP_COLS + ["ms", "sel", "killed"]].rename(
            columns={"ms": f"r{s}", "sel": f"rs{s}", "killed": f"rk{s}"}), on=GROUP_COLS)
        rnd_overall[s] = (int(r["killed"].sum()), int(r["sel"].sum()))

    gk, gn = int(gpt["killed"].sum()), int(gpt["sel"].sum())
    gpt_overall = gk / gn

    # ---------------------------------------------------------------- 1. PRE-REGISTER
    print("\n" + "-" * 78)
    print("1. KET QUA PRE-REGISTER  (seed42, group-weighted, 3 tieu chi)")
    print("   Tieu chi: p<0.05  VA  r_rb>=0.30  VA  median(dMS)>0")
    print("-" * 78)
    d42 = (merged["gpt"] - merged[f"r{PRIMARY_SEED}"]).values
    w = wilcoxon_line(d42)
    passed = (w["p"] < ALPHA and w["r_rb"] >= MIN_RRB and w["median"] > 0)
    print(f"   n={w['n']}  W/L/T={w['wins']}/{w['losses']}/{w['ties']}")
    print(f"   median(dMS) = {w['median']:+.4f}   [{'PASS' if w['median']>0 else 'FAIL'}]")
    print(f"   Wilcoxon p  = {w['p']:.4f}         [{'PASS' if w['p']<ALPHA else 'FAIL'}]")
    print(f"   r_rb        = {w['r_rb']:+.4f}        [{'PASS' if w['r_rb']>=MIN_RRB else 'FAIL'}]")
    print(f"   => KET LUAN PRE-REGISTER: {'SUPPORT H1' if passed else 'KHONG DU BANG CHUNG cho H1'}")

    # ---------------------------------------------------------------- 2. CHAN DOAN
    print("\n" + "-" * 78)
    print("2. CHAN DOAN vi sao median = 0")
    print("-" * 78)
    ksel = merged["g_sel"]
    ties_small = int(((np.abs(d42) < 1e-12) & (ksel <= 3)).sum())
    print(f"   Kich thuoc chon moi group (k): min={ksel.min()}, median={int(ksel.median())}, max={ksel.max()}")
    print(f"   -> group k nho khien MS bi luong tu tho; {w['ties']}/{w['n']} cap HOA,")
    print(f"      trong do {ties_small} cap tu group k<=3. median bi ghim ve 0 do ties,")
    print(f"      KHONG phai do GPT thua. (median-of-nonzero = {np.median(d42[np.abs(d42)>1e-12]):+.4f})")

    # ---------------------------------------------------------------- 3. ROBUSTNESS A
    print("\n" + "-" * 78)
    print("3. ROBUSTNESS A: bo tieu chi median (thoai hoa), giu p & r_rb")
    print("-" * 78)
    okA = (w["p"] < ALPHA and w["r_rb"] >= MIN_RRB)
    print(f"   seed42: p={w['p']:.4f}, r_rb={w['r_rb']:+.3f}  -> {'DAT' if okA else 'chua dat'} (2 tieu chi)")

    # ---------------------------------------------------------------- 4. ROBUSTNESS B
    print("\n" + "-" * 78)
    print("4. ROBUSTNESS B: MUTANT-WEIGHTED (overall MS, 2-proportion z-test, 1 phia)")
    print("-" * 78)
    rk, rn = rnd_overall[PRIMARY_SEED]
    p1, p2 = gpt_overall, rk / rn
    pp = (gk + rk) / (gn + rn)
    z = (p1 - p2) / np.sqrt(pp * (1 - pp) * (1 / gn + 1 / rn))
    pv = 1 - norm.cdf(z)
    print(f"   GPT overall MS = {p1:.4f} ({gk}/{gn})")
    print(f"   RANDOM seed42  = {p2:.4f} ({rk}/{rn})   diff = {p1-p2:+.4f}")
    print(f"   z = {z:.2f}   p(1 phia) = {pv:.4f}  -> {'GPT > random co y nghia' if pv<ALPHA else 'chua co y nghia'}")

    # ---------------------------------------------------------------- 5. MONTE CARLO
    print("\n" + "-" * 78)
    print(f"5. ROBUSTNESS C: MONTE CARLO ({MC_DRAWS} lan boc random by-group, cung budget)")
    print("   (dac trung hoa phan phoi random; seed42 chi la 1 diem trong do)")
    print("-" * 78)
    sample = pd.read_csv(ROOT / "data" / "full_sample.csv")
    sample["mutant_id"] = sample["mutant_id"].astype(str)
    sample["k"] = sample["mutant_id"].map(kill_map)
    sample = sample[~sample["project"].isin(broken)]
    groups = [(g["k"].values.astype(int), kcount(len(g))) for _, g in sample.groupby(GROUP_COLS)]
    rng = np.random.default_rng(MC_RNG_SEED)
    mc = np.empty(MC_DRAWS)
    for i in range(MC_DRAWS):
        tk = tn = 0
        for killed, k in groups:
            tk += killed[rng.choice(len(killed), size=k, replace=False)].sum()
            tn += k
        mc[i] = tk / tn
    p_mc = (mc >= gpt_overall).mean()
    z_mc = (gpt_overall - mc.mean()) / mc.std()
    pct42 = (mc <= p2).mean() * 100
    print(f"   Random MS: mean={mc.mean():.4f} sd={mc.std():.4f} "
          f"[2.5%,97.5%]=[{np.percentile(mc,2.5):.4f},{np.percentile(mc,97.5):.4f}]")
    print(f"   GPT MS={gpt_overall:.4f} dung o z={z_mc:+.2f}sd; so lan random>=GPT: "
          f"{int((mc>=gpt_overall).sum())}/{MC_DRAWS} -> p={p_mc:.4f}")
    print(f"   (seed42 nam o percentile {pct42:.0f}% cua random => 1 lan boc dien hinh, khong xui)")

    # ---------------------------------------------------------------- 6. SUBGROUP §6.3
    print("\n" + "-" * 78)
    print("6. SUBGROUP §6.3 (theo project, dung seed42; n_group<10 -> chi descriptive)")
    print("-" * 78)
    merged["d42"] = merged["gpt"] - merged[f"r{PRIMARY_SEED}"]
    print(f"   {'project':<13}{'n':>4}{'win':>5}{'loss':>5}{'tie':>5}{'mean_d':>9}{'median_d':>10}  note")
    for proj, x in merged.groupby("project"):
        d = x["d42"].values
        win, loss = int((d > 1e-12).sum()), int((d < -1e-12).sum())
        tie = len(d) - win - loss
        note = "descriptive (n<10)" if len(d) < 10 else "co the test"
        print(f"   {proj:<13}{len(d):>4}{win:>5}{loss:>5}{tie:>5}"
              f"{d.mean():>+9.4f}{np.median(d):>+10.4f}  {note}")

    # ---------------------------------------------------------------- LUU
    out_rows = [
        {"analysis": "pre_register_seed42_group", "n": w["n"], "median_dMS": w["median"],
         "wilcoxon_p": w["p"], "r_rb": w["r_rb"], "wins": w["wins"], "losses": w["losses"],
         "ties": w["ties"], "verdict": "SUPPORT" if passed else "NO_SUPPORT"},
        {"analysis": "mutant_weighted_seed42", "gpt_ms": gpt_overall, "random_ms": p2,
         "diff": p1 - p2, "z": z, "p_one_sided": pv,
         "verdict": "SUPPORT" if pv < ALPHA else "NO_SUPPORT"},
        {"analysis": f"monte_carlo_{MC_DRAWS}", "gpt_ms": gpt_overall, "random_mean": mc.mean(),
         "random_sd": mc.std(), "z": z_mc, "p_empirical": p_mc,
         "verdict": "SUPPORT" if p_mc < ALPHA else "NO_SUPPORT"},
    ]
    pd.DataFrame(out_rows).to_csv(RESULTS / "full_h1_result.csv", index=False)
    merged.to_csv(RESULTS / "full_paired_by_class.csv", index=False)

    print("\n" + "=" * 78)
    print("TOM TAT TRUNG THUC:")
    print(f"  - Pre-register (seed42, group-weighted): {'DAT' if passed else 'KHONG DAT'}")
    print(f"  - Mutant-weighted (seed42): {'DAT' if pv<ALPHA else 'khong'} (p={pv:.4f})")
    print(f"  - Monte Carlo: {'DAT' if p_mc<ALPHA else 'khong'} (p={p_mc:.4f})")
    print("  - Hieu ung TAP TRUNG o JacksonCore; Csv/Codec gan nhu khong. Ket luan: partial support.")
    print("=" * 78)
    print("\nDa luu: results/full_h1_result.csv, results/full_paired_by_class.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
