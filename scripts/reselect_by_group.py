"""Re-derive full_gpt_selected.csv / full_random_selected.csv using
selection_scope=by_group instead of global.

Why: the original global top-10% selection sorted the whole pool by the
GPT usefulness_score (a coarse 1-5 integer) and broke ties by mutant_id
ascending. Because "Lang_..." sorts before "Math_..." and there were far
more Lang mutants tied at the top score than the whole selection budget,
the global GPT selection ended up with 0 Math mutants - making it
impossible to test H1/RQ3 on Math. Grouping by (project, version,
class_name) before taking the top 10% guarantees every group gets its
proportional share.

No new OpenAI calls are made: full_llm_output.csv already has
usefulness_score for all 50,694 mutants, and PIT ground truth already
covers the full pool, so only the *selection* step is redone.
"""
from __future__ import annotations

import pandas as pd

from random_baseline import random_select_by_group
from utils import ensure_parent, load_config, resolve_path, select_top


def main() -> int:
    cfg = load_config()
    if cfg.get("selection_scope") != "by_group":
        raise SystemExit("config.yaml selection_scope must be 'by_group' before running this script.")

    sample = pd.read_csv(resolve_path(cfg["input_file"]))
    llm_output = pd.read_csv(resolve_path(cfg["gpt_ranking_output"]))

    gpt_selected = select_top(llm_output, cfg).copy()
    gpt_selected["selected_by"] = "gpt4o_mini"

    seed = int(cfg.get("random_seed", 42))
    random_selected = random_select_by_group(sample, cfg, seed).copy()
    random_selected["selected_by"] = "random"

    gpt_out = resolve_path(cfg["gpt_selected_output"])
    random_out = resolve_path(cfg["random_selected_output"])
    ensure_parent(gpt_out)
    ensure_parent(random_out)
    gpt_selected.to_csv(gpt_out, index=False, encoding="utf-8")
    random_selected.to_csv(random_out, index=False, encoding="utf-8")

    print(f"Saved: {gpt_out} ({len(gpt_selected)} rows)")
    print(f"Saved: {random_out} ({len(random_selected)} rows)")

    print("\nGPT selected by project:")
    print(gpt_selected["project"].value_counts())
    print("\nRandom selected by project:")
    print(random_selected["project"].value_counts())

    group_cols = cfg["group_columns"]
    n_groups_total = sample.groupby(group_cols, dropna=False).ngroups
    n_groups_gpt = gpt_selected.groupby(group_cols, dropna=False).ngroups
    n_groups_random = random_selected.groupby(group_cols, dropna=False).ngroups
    print(f"\nGroups in pool ({'+'.join(group_cols)}): {n_groups_total}")
    print(f"Groups represented in GPT selection: {n_groups_gpt}")
    print(f"Groups represented in Random selection: {n_groups_random}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
