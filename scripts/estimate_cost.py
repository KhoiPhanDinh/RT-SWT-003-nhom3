from __future__ import annotations

import pandas as pd

from utils import load_config, resolve_path


def main() -> int:
    cfg = load_config()
    cost_path = resolve_path(cfg["cost_log_file"])

    if not cost_path.exists():
        print(f"Cost log not found: {cost_path}")
        return 1

    df = pd.read_csv(cost_path)

    numeric_cols = [
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "estimated_cost_usd",
        "estimated_cost_vnd",
        "latency_seconds",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    print("Cost summary")
    print("-" * 40)
    print(f"Batches: {len(df)}")
    print(f"Prompt tokens: {int(df['prompt_tokens'].sum()) if 'prompt_tokens' in df else 0}")
    print(f"Completion tokens: {int(df['completion_tokens'].sum()) if 'completion_tokens' in df else 0}")
    print(f"Total tokens: {int(df['total_tokens'].sum()) if 'total_tokens' in df else 0}")
    print(f"Estimated USD: {df['estimated_cost_usd'].sum() if 'estimated_cost_usd' in df else 0:.6f}")
    print(f"Estimated VND: {df['estimated_cost_vnd'].sum() if 'estimated_cost_vnd' in df else 0:.0f}")
    print(f"Total latency seconds: {df['latency_seconds'].sum() if 'latency_seconds' in df else 0:.3f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
