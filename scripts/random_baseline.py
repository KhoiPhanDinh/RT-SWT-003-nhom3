from __future__ import annotations

import hashlib
import random

import pandas as pd

from utils import (
    ensure_parent,
    get_input_file,
    load_config,
    read_mutant_pool,
    resolve_path,
    selected_count,
    validate_mutant_pool,
)


def random_select_global(df: pd.DataFrame, k: int, seed: int) -> pd.DataFrame:
    rng = random.Random(seed)
    indices = list(df.index)
    chosen = rng.sample(indices, k)
    return df.loc[chosen].copy()


def stable_group_seed(seed: int, group_key) -> int:
    """Deterministic 32-bit seed derived from (seed, group_key).

    Python's built-in hash() salts str hashing per-process (PYTHONHASHSEED
    randomization, default since Python 3.3), so hash((seed, str(group_key)))
    is NOT reproducible across runs/machines even with the same seed. Use a
    fixed-algorithm hash (sha256) instead so the random baseline is actually
    reproducible as required by proposal §5.5/§7.1/§7.4.
    """
    payload = f"{seed}|{group_key}".encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    return int(digest[:8], 16)


def random_select_by_group(df: pd.DataFrame, cfg: dict, seed: int) -> pd.DataFrame:
    top_percent = float(cfg.get("top_percent", 10))
    group_cols = [c for c in cfg.get("group_columns", []) if c in df.columns]
    if not group_cols:
        raise ValueError("selection_scope is by_group but no valid group_columns exist in data.")

    selected_parts = []
    for group_key, group in df.groupby(group_cols, dropna=False):
        k = selected_count(len(group), top_percent)
        # Deterministic per group, derived from main seed + group key.
        group_seed = stable_group_seed(seed, group_key)
        selected_parts.append(random_select_global(group, k, group_seed))

    return pd.concat(selected_parts, ignore_index=True)


def main() -> int:
    cfg = load_config()
    input_path = get_input_file(cfg)
    df = read_mutant_pool(input_path)

    errors = validate_mutant_pool(df)
    if errors:
        print("[ERROR] Invalid mutant pool. Run scripts/validate_mutant_pool.py first.")
        for e in errors:
            print(f"- {e}")
        return 1

    seed = int(cfg.get("random_seed", 42))
    selection_scope = cfg.get("selection_scope", "global")

    gpt_selected_path = resolve_path(cfg["gpt_selected_output"])
    if gpt_selected_path.exists() and selection_scope == "global":
        # Ensure random subset has exactly the same size as GPT subset.
        k = len(pd.read_csv(gpt_selected_path))
    else:
        k = selected_count(len(df), float(cfg.get("top_percent", 10)))

    if selection_scope == "by_group":
        selected = random_select_by_group(df, cfg, seed)
    else:
        selected = random_select_global(df, k, seed)

    selected = selected.copy()
    selected["selection_strategy"] = f"random_seed_{seed}"
    selected["selected_by"] = "random"

    output_path = resolve_path(cfg["random_selected_output"])
    ensure_parent(output_path)
    selected.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Saved random selected: {output_path}")
    print(f"Random seed: {seed}")
    print(f"Total mutants: {len(df)}")
    print(f"Selected mutants: {len(selected)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
