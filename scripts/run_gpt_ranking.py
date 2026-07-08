from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from openai import OpenAI
from tqdm import tqdm

from utils import (
    ensure_parent,
    estimate_cost_usd,
    extract_json_array,
    get_input_file,
    load_config,
    load_env,
    make_mutant_payload,
    read_mutant_pool,
    resolve_path,
    safe_int_score,
    select_top,
    validate_mutant_pool,
)


def build_user_prompt(base_prompt: str, batch_df: pd.DataFrame) -> str:
    payload = make_mutant_payload(batch_df)
    return (
        base_prompt.strip()
        + "\n\n"
        + "Mutants to rank:\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )


def dry_run_rank(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for index, row in df.reset_index(drop=True).iterrows():
        score = 5 - (index % 5)
        rows.append({
            "mutant_id": row["mutant_id"],
            "usefulness_score": score,
            "short_reason": "DRY_RUN fake score for pipeline testing only.",
            "api_status": "dry_run",
            "checkpoint_status": "dry_run",
        })
    return pd.DataFrame(rows)


def load_checkpoint(checkpoint_path: Path) -> pd.DataFrame:
    if not checkpoint_path.exists():
        return pd.DataFrame()

    rows = []
    with checkpoint_path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"[WARN] Invalid checkpoint line {line_no}; skipped.")

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    if "mutant_id" in df.columns:
        df["mutant_id"] = df["mutant_id"].astype(str)
        df = df.drop_duplicates(subset=["mutant_id"], keep="last")
    return df


def append_checkpoint(checkpoint_path: Path, rows: list[dict[str, Any]]) -> None:
    ensure_parent(checkpoint_path)
    with checkpoint_path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()


def append_cost_rows(cost_log_path: Path, cost_rows: list[dict[str, Any]]) -> None:
    ensure_parent(cost_log_path)
    new_df = pd.DataFrame(cost_rows)
    if cost_log_path.exists() and cost_log_path.stat().st_size > 0:
        old_df = pd.read_csv(cost_log_path)
        out_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        out_df = new_df
    out_df.to_csv(cost_log_path, index=False, encoding="utf-8")


def append_api_log(api_log_path: Path, text: str) -> None:
    ensure_parent(api_log_path)
    with api_log_path.open("a", encoding="utf-8") as f:
        f.write(text)


def call_openai_batch(
    client: OpenAI,
    cfg: dict,
    base_prompt: str,
    batch_df: pd.DataFrame,
    api_log_path: Path,
    cost_log_path: Path,
    checkpoint_path: Path,
    batch_index: int,
) -> None:
    model = cfg["model"]
    temperature = float(cfg.get("temperature", 0))
    top_p = float(cfg.get("top_p", 1))
    user_prompt = build_user_prompt(base_prompt, batch_df)

    started = time.time()
    timestamp = datetime.now().isoformat(timespec="seconds")
    batch_ids = list(batch_df["mutant_id"].astype(str))

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            top_p=top_p,
            messages=[
                {
                    "role": "system",
                    "content": "You are a careful mutation testing research assistant. Return valid JSON only.",
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        latency = time.time() - started
        content = response.choices[0].message.content or ""
        parsed = extract_json_array(content)

        prompt_tokens = int(getattr(response.usage, "prompt_tokens", 0) or 0)
        completion_tokens = int(getattr(response.usage, "completion_tokens", 0) or 0)
        total_tokens = int(getattr(response.usage, "total_tokens", 0) or 0)
        estimated_cost = estimate_cost_usd(prompt_tokens, completion_tokens, cfg)
        estimated_cost_vnd = estimated_cost * float(cfg.get("usd_to_vnd", 25000))

        append_cost_rows(cost_log_path, [{
            "timestamp": timestamp,
            "model": model,
            "batch_index": batch_index,
            "batch_size": len(batch_ids),
            "mutant_ids": "|".join(batch_ids),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": estimated_cost,
            "estimated_cost_vnd": estimated_cost_vnd,
            "latency_seconds": round(latency, 3),
            "status": "success",
            "error_message": "",
        }])

        append_api_log(
            api_log_path,
            "=" * 80 + "\n"
            + f"timestamp: {timestamp}\n"
            + f"model: {model}\n"
            + f"batch_index: {batch_index}\n"
            + f"temperature: {temperature}\n"
            + f"top_p: {top_p}\n"
            + f"mutant_ids: {batch_ids}\n"
            + f"prompt_tokens: {prompt_tokens}\n"
            + f"completion_tokens: {completion_tokens}\n"
            + f"total_tokens: {total_tokens}\n"
            + f"estimated_cost_usd: {estimated_cost}\n"
            + f"latency_seconds: {round(latency, 3)}\n"
            + "status: success\n"
            + "raw_response:\n"
            + content + "\n"
        )

        parsed_by_id = {}
        for item in parsed:
            mid = str(item.get("mutant_id", "")).strip()
            if mid:
                parsed_by_id[mid] = item

        missing_ids = [mid for mid in batch_ids if mid not in parsed_by_id]
        if missing_ids:
            raise ValueError(
                "GPT response did not include all requested mutant_id values. "
                f"Missing: {missing_ids}. Batch not checkpointed."
            )

        checkpoint_rows = []
        for mid in batch_ids:
            item = parsed_by_id[mid]
            checkpoint_rows.append({
                "mutant_id": mid,
                "usefulness_score": safe_int_score(item.get("usefulness_score", 1)),
                "short_reason": str(item.get("short_reason", "")).strip(),
                "api_status": "success",
                "checkpoint_status": "done",
                "timestamp": timestamp,
                "model": model,
                "batch_index": batch_index,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "estimated_cost_usd": estimated_cost,
                "latency_seconds": round(latency, 3),
            })

        # Important: save immediately after successful API batch.
        append_checkpoint(checkpoint_path, checkpoint_rows)
        print(f"[CHECKPOINT] Saved {len(checkpoint_rows)} rows to {checkpoint_path}")

    except Exception as e:
        latency = time.time() - started
        error_message = str(e)

        append_cost_rows(cost_log_path, [{
            "timestamp": timestamp,
            "model": model,
            "batch_index": batch_index,
            "batch_size": len(batch_ids),
            "mutant_ids": "|".join(batch_ids),
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0,
            "estimated_cost_vnd": 0,
            "latency_seconds": round(latency, 3),
            "status": "error",
            "error_message": error_message,
        }])

        append_api_log(
            api_log_path,
            "=" * 80 + "\n"
            + f"timestamp: {timestamp}\n"
            + f"model: {model}\n"
            + f"batch_index: {batch_index}\n"
            + f"mutant_ids: {batch_ids}\n"
            + f"latency_seconds: {round(latency, 3)}\n"
            + "status: error\n"
            + f"error_message: {error_message}\n"
            + "checkpoint: not_written_for_failed_batch\n"
        )

        raise RuntimeError(
            f"API batch failed at batch_index={batch_index}. "
            "Previous successful batches were checkpointed. "
            "After topping up/fixing the issue, rerun python scripts/run_pipeline.py to resume. "
            f"Original error: {error_message}"
        ) from e


def main() -> int:
    cfg = load_config()
    load_env()

    input_path = get_input_file(cfg)
    df = read_mutant_pool(input_path)
    errors = validate_mutant_pool(df)
    if errors:
        print("[ERROR] Invalid mutant pool. Run scripts/validate_mutant_pool.py first.")
        for e in errors:
            print(f"- {e}")
        return 1

    prompt_path = resolve_path(cfg["prompt_file"])
    base_prompt = prompt_path.read_text(encoding="utf-8")

    ranking_output = resolve_path(cfg["gpt_ranking_output"])
    selected_output = resolve_path(cfg["gpt_selected_output"])
    api_log_path = resolve_path(cfg["api_log_file"])
    cost_log_path = resolve_path(cfg["cost_log_file"])
    checkpoint_path = resolve_path(cfg.get("checkpoint_file", "results/pilot_gpt_checkpoint.jsonl"))

    for p in [ranking_output, selected_output, api_log_path, cost_log_path, checkpoint_path]:
        ensure_parent(p)

    dry_run = bool(cfg.get("dry_run", False))
    batch_size = int(cfg.get("batch_size", 10))
    resume_enabled = bool(cfg.get("resume_enabled", True))
    reset_checkpoint = bool(cfg.get("reset_checkpoint", False))

    if reset_checkpoint and checkpoint_path.exists():
        checkpoint_path.unlink()
        print(f"[RESET] Deleted checkpoint file: {checkpoint_path}")

    if dry_run:
        print("[WARN] dry_run=true. No API call will be made. Output is fake and only for testing pipeline.")
        ranking_df = dry_run_rank(df)
        api_log_path.write_text(
            "DRY_RUN=true. No OpenAI API call was made. Do not use this output as research result.\n",
            encoding="utf-8",
        )
        pd.DataFrame([{
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "model": cfg["model"],
            "batch_index": 0,
            "batch_size": len(df),
            "mutant_ids": "DRY_RUN",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0,
            "estimated_cost_vnd": 0,
            "latency_seconds": 0,
            "status": "dry_run",
            "error_message": "",
        }]).to_csv(cost_log_path, index=False, encoding="utf-8")

    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[ERROR] OPENAI_API_KEY not found. Create .env from .env.example before real run.")
            return 1

        client = OpenAI(api_key=api_key)

        checkpoint_df = load_checkpoint(checkpoint_path) if resume_enabled else pd.DataFrame()
        done_ids = set(checkpoint_df["mutant_id"].astype(str)) if not checkpoint_df.empty else set()

        df["mutant_id"] = df["mutant_id"].astype(str)
        pending_df = df[~df["mutant_id"].isin(done_ids)].copy()

        print(f"[RESUME] Checkpoint file: {checkpoint_path}")
        print(f"[RESUME] Total mutants: {len(df)}")
        print(f"[RESUME] Already done: {len(done_ids)}")
        print(f"[RESUME] Pending: {len(pending_df)}")

        if len(pending_df) > 0:
            batch_index = 0
            for start in tqdm(range(0, len(pending_df), batch_size), desc="GPT ranking pending batches"):
                batch_df = pending_df.iloc[start:start + batch_size].copy()
                call_openai_batch(
                    client=client,
                    cfg=cfg,
                    base_prompt=base_prompt,
                    batch_df=batch_df,
                    api_log_path=api_log_path,
                    cost_log_path=cost_log_path,
                    checkpoint_path=checkpoint_path,
                    batch_index=batch_index,
                )
                batch_index += 1

        checkpoint_df = load_checkpoint(checkpoint_path)
        if checkpoint_df.empty:
            print("[ERROR] No checkpoint results found after API run.")
            return 1

        done_ids = set(checkpoint_df["mutant_id"].astype(str))
        missing_after_run = sorted(set(df["mutant_id"].astype(str)) - done_ids)
        if missing_after_run:
            print("[ERROR] Run is incomplete. Some mutants are still missing from checkpoint.")
            print(f"Missing count: {len(missing_after_run)}")
            print("First missing IDs:", missing_after_run[:20])
            print("Rerun the same command after fixing quota/billing/network issue.")
            return 2

        ranking_df = checkpoint_df.copy()

    ranking_df["mutant_id"] = ranking_df["mutant_id"].astype(str)
    df["mutant_id"] = df["mutant_id"].astype(str)

    keep_cols = [
        "mutant_id",
        "usefulness_score",
        "short_reason",
        "api_status",
        "checkpoint_status",
        "timestamp",
        "model",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "estimated_cost_usd",
        "latency_seconds",
    ]
    keep_cols = [c for c in keep_cols if c in ranking_df.columns]

    merged = df.merge(ranking_df[keep_cols], on="mutant_id", how="left")
    merged["usefulness_score"] = merged["usefulness_score"].fillna(1).apply(safe_int_score)
    merged["short_reason"] = merged["short_reason"].fillna("Missing GPT score.")
    merged["api_status"] = merged["api_status"].fillna("missing")
    merged["checkpoint_status"] = merged["checkpoint_status"].fillna("missing")

    merged = merged.sort_values(
        by=["usefulness_score", "mutant_id"],
        ascending=[False, True],
    ).reset_index(drop=True)
    merged["rank"] = range(1, len(merged) + 1)

    selected = select_top(merged, cfg).copy()
    selected["selected_by"] = "gpt4o_mini"

    merged.to_csv(ranking_output, index=False, encoding="utf-8")
    selected.to_csv(selected_output, index=False, encoding="utf-8")

    print(f"Saved GPT ranking: {ranking_output}")
    print(f"Saved GPT selected: {selected_output}")
    print(f"Saved API log: {api_log_path}")
    print(f"Saved cost log: {cost_log_path}")
    print(f"Checkpoint file: {checkpoint_path}")
    print(f"Total mutants: {len(df)}")
    print(f"Selected mutants: {len(selected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
