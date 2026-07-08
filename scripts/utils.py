from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from dotenv import load_dotenv


REQUIRED_COLUMNS = [
    "mutant_id",
    "project",
    "version",
    "class_name",
    "mutation_operator",
    "original_code",
    "mutated_code",
    "surrounding_context",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_path(path_str: str) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    return project_root() / p


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    if config_path is None:
        config_path = project_root() / "config.yaml"
    else:
        config_path = Path(config_path)

    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    return cfg


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_env() -> None:
    load_dotenv(project_root() / ".env")


def get_input_file(cfg: dict[str, Any]) -> Path:
    input_file = resolve_path(cfg["input_file"])
    if input_file.exists():
        return input_file

    fallback = resolve_path(cfg.get("fallback_input_file", "data/sample_mutant_pool.csv"))
    if fallback.exists():
        print(f"[WARN] {input_file} not found. Using fallback file: {fallback}")
        return fallback

    raise FileNotFoundError(
        f"Input file not found: {input_file}. Fallback file also not found: {fallback}"
    )


def read_mutant_pool(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def validate_mutant_pool(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")

    if "mutant_id" in df.columns:
        duplicate_count = int(df["mutant_id"].duplicated().sum())
        if duplicate_count > 0:
            errors.append(f"Duplicate mutant_id count: {duplicate_count}")

    if len(df) == 0:
        errors.append("Mutant pool is empty.")

    for col in REQUIRED_COLUMNS:
        if col in df.columns:
            missing_values = int(df[col].isna().sum())
            empty_values = int((df[col].astype(str).str.strip() == "").sum())
            total_bad = missing_values + empty_values
            if total_bad > 0:
                errors.append(f"Column '{col}' has {total_bad} missing/empty values.")

    return errors


def safe_int_score(value: Any) -> int:
    try:
        score = int(float(value))
    except Exception:
        return 1
    return max(1, min(5, score))


def selected_count(n: int, top_percent: float) -> int:
    return max(1, math.ceil(n * top_percent / 100.0))


def select_top(df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    top_percent = float(cfg.get("top_percent", 10))
    selection_scope = cfg.get("selection_scope", "global")

    if selection_scope == "by_group":
        group_cols = [c for c in cfg.get("group_columns", []) if c in df.columns]
        if not group_cols:
            raise ValueError("selection_scope is by_group but no valid group_columns exist in data.")

        selected_parts = []
        for _, group in df.groupby(group_cols, dropna=False):
            k = selected_count(len(group), top_percent)
            selected_parts.append(
                group.sort_values(
                    by=["usefulness_score", "mutant_id"],
                    ascending=[False, True],
                ).head(k)
            )
        selected = pd.concat(selected_parts, ignore_index=True)
    else:
        k = selected_count(len(df), top_percent)
        selected = df.sort_values(
            by=["usefulness_score", "mutant_id"],
            ascending=[False, True],
        ).head(k).copy()

    selected["selection_strategy"] = "gpt4o_mini_top_percent"
    return selected


def extract_json_array(text: str) -> list[dict[str, Any]]:
    text = text.strip()

    # Remove common Markdown fences if the model accidentally returns them.
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            for key in ("mutants", "results", "ranking"):
                if isinstance(parsed.get(key), list):
                    return parsed[key]
    except json.JSONDecodeError:
        pass

    # Fallback: find the first JSON array substring.
    match = re.search(r"\[.*\]", text, flags=re.DOTALL)
    if match:
        parsed = json.loads(match.group(0))
        if isinstance(parsed, list):
            return parsed

    raise ValueError("Could not parse GPT output as JSON array.")


def estimate_cost_usd(
    prompt_tokens: int,
    completion_tokens: int,
    cfg: dict[str, Any],
) -> float:
    input_rate = float(cfg.get("price_per_1m_input_usd", 0) or 0)
    output_rate = float(cfg.get("price_per_1m_output_usd", 0) or 0)

    return (
        prompt_tokens / 1_000_000 * input_rate
        + completion_tokens / 1_000_000 * output_rate
    )


def make_mutant_payload(df: pd.DataFrame) -> list[dict[str, Any]]:
    keep_cols = [
        "mutant_id",
        "project",
        "version",
        "class_name",
        "method_name",
        "line_number",
        "mutation_operator",
        "original_code",
        "mutated_code",
        "surrounding_context",
    ]

    existing_cols = [c for c in keep_cols if c in df.columns]
    return df[existing_cols].fillna("").to_dict(orient="records")
