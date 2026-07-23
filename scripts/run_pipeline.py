import csv
import hashlib
import json
import math
import os
import random
import re
import time
from pathlib import Path

import pandas as pd
import yaml
from dotenv import load_dotenv
from tqdm import tqdm


ROOT = Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))

DATA_PATH = ROOT / CONFIG["data"]["sample_path"]
RESULTS_DIR = ROOT / CONFIG["output"]["results_dir"]
LOGS_DIR = ROOT / CONFIG["output"]["logs_dir"]

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_CFG = CONFIG.get("checkpoint", {})
CHECKPOINT_ENABLED = bool(CHECKPOINT_CFG.get("enabled", True))
RESUME_FROM_CHECKPOINT = bool(CHECKPOINT_CFG.get("resume", True))
SAVE_EVERY_BATCH = bool(CHECKPOINT_CFG.get("save_every_batch", True))

CHECKPOINT_PATH = ROOT / CHECKPOINT_CFG.get("path", "logs/full_gpt_checkpoint.jsonl")
API_LOG_PATH = ROOT / CHECKPOINT_CFG.get("api_log_path", "logs/full_api_log.csv")
RANDOM_LOG_PATH = LOGS_DIR / "full_random_log.csv"

LLM_OUTPUT_PATH = RESULTS_DIR / "full_llm_output.csv"
GPT_SELECTED_PATH = RESULTS_DIR / "full_gpt_selected.csv"

PROMPT_PATH = ROOT / "ranking_prompt.txt"


def stable_hash_int(text: str) -> int:
    return int(hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest()[:8], 16)


def load_checkpoint() -> dict:
    done = {}
    if not CHECKPOINT_ENABLED or not RESUME_FROM_CHECKPOINT:
        return done

    if CHECKPOINT_PATH.exists():
        with CHECKPOINT_PATH.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    done[str(obj["mutant_id"])] = obj
                except Exception:
                    print(f"[WARN] Bad checkpoint line ignored: {line_no}")
                    continue
    return done


def append_checkpoint(rows):
    if not CHECKPOINT_ENABLED:
        return

    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CHECKPOINT_PATH.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def ensure_api_log_header():
    API_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not API_LOG_PATH.exists():
        with API_LOG_PATH.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "model", "batch_size", "input_tokens",
                "output_tokens", "total_tokens", "status", "error"
            ])


def log_api(model, batch_size, usage=None, status="OK", error=""):
    ensure_api_log_header()
    usage = usage or {}
    with API_LOG_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            model,
            batch_size,
            usage.get("prompt_tokens", usage.get("input_tokens", "")),
            usage.get("completion_tokens", usage.get("output_tokens", "")),
            usage.get("total_tokens", ""),
            status,
            error[:500],
        ])


def make_mutant_payload(row):
    return {
        "mutant_id": str(row["mutant_id"]),
        "project": str(row["project"]),
        "version": str(row["version"]),
        "class_name": str(row["class_name"]),
        "method_name": str(row["method_name"]),
        "line_number": str(row["line_number"]),
        "mutation_operator": str(row["mutation_operator"]),
        "original_code": str(row["original_code"])[:1000],
        "mutated_code": str(row["mutated_code"])[:1000],
        "surrounding_context": str(row["surrounding_context"])[:2500],
    }


def dry_run_score(payload):
    text = " ".join([
        payload.get("mutation_operator", ""),
        payload.get("original_code", ""),
        payload.get("mutated_code", ""),
        payload.get("surrounding_context", ""),
    ])
    h = stable_hash_int(payload["mutant_id"] + text)

    score = 2 + (h % 3)  # 2..4 baseline

    op = payload.get("mutation_operator", "").lower()
    code = payload.get("original_code", "").lower()

    if any(x in op for x in ["conditionals", "return", "math", "increments", "negate"]):
        score += 1
    if any(x in code for x in ["if", "return", "throw", "while", "for", "switch", "case"]):
        score += 1
    if len(payload.get("surrounding_context", "")) < 30:
        score -= 1

    score = max(1, min(5, score))
    confidence = 3 + (h % 3)
    confidence = max(1, min(5, confidence))

    return {
        "mutant_id": payload["mutant_id"],
        "score": score,
        "confidence": confidence,
        "rationale": "dry-run deterministic heuristic; replace with GPT run for final results",
        "raw_response": "",
    }


def extract_json_array(text: str):
    text = text.strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass

    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        raise ValueError("No JSON array found in model response.")

    return json.loads(match.group(0))


def call_openai_batch(client, model, system_prompt, payloads, temperature, max_retries, timeout_seconds):
    user_content = (
        "Rank the following Java PIT mutants.\n"
        "Return JSON array only. Mutants:\n"
        + json.dumps(payloads, ensure_ascii=False)
    )

    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                timeout=timeout_seconds,
            )

            content = response.choices[0].message.content or ""
            usage = {}
            if getattr(response, "usage", None):
                usage = {
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", ""),
                    "completion_tokens": getattr(response.usage, "completion_tokens", ""),
                    "total_tokens": getattr(response.usage, "total_tokens", ""),
                }

            parsed = extract_json_array(content)

            by_id = {str(x.get("mutant_id")): x for x in parsed if isinstance(x, dict)}
            out = []

            for payload in payloads:
                mid = payload["mutant_id"]
                item = by_id.get(mid)
                if item is None:
                    item = {
                        "mutant_id": mid,
                        "score": 1,
                        "confidence": 1,
                        "rationale": "missing from model response",
                    }

                out.append({
                    "mutant_id": mid,
                    "score": int(item.get("score", 1)),
                    "confidence": int(item.get("confidence", 1)),
                    "rationale": str(item.get("rationale", ""))[:300],
                    "raw_response": content[:2000],
                })

            log_api(model, len(payloads), usage=usage, status="OK")
            return out

        except Exception as e:
            last_error = e
            log_api(model, len(payloads), status="ERROR", error=str(e))
            time.sleep(min(30, 2 ** attempt))

    raise RuntimeError(f"OpenAI batch failed after retries: {last_error}")


def normalize_rank_output(df):
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(1).clip(1, 5)
    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(1).clip(1, 5)
    df = df.sort_values(
        by=["score", "confidence", "mutant_id"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)
    return df


def save_current_outputs(sample, done, k):
    if not done:
        return

    llm_df = pd.DataFrame(done.values())
    llm_df["mutant_id"] = llm_df["mutant_id"].astype(str)

    merged = sample.merge(llm_df, on="mutant_id", how="inner")
    merged = normalize_rank_output(merged)
    merged.to_csv(LLM_OUTPUT_PATH, index=False)

    current_k = min(k, len(merged))
    merged.head(current_k).to_csv(GPT_SELECTED_PATH, index=False)


def main():
    print("=" * 60)
    print("RUN FULL LR PIPELINE WITH CHECKPOINT")
    print("=" * 60)

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing full sample: {DATA_PATH}")

    sample = pd.read_csv(DATA_PATH)
    sample["mutant_id"] = sample["mutant_id"].astype(str)

    fraction = float(CONFIG["selection"]["fraction"])
    min_k = int(CONFIG["selection"].get("min_k", 1))
    k = max(min_k, math.ceil(len(sample) * fraction))

    model = CONFIG["llm"]["model"]
    dry_run = bool(CONFIG["llm"]["dry_run"])
    batch_size = int(CONFIG["llm"].get("batch_size", 8))
    temperature = float(CONFIG["llm"].get("temperature", 0))
    max_retries = int(CONFIG["llm"].get("max_retries", 4))
    timeout_seconds = int(CONFIG["llm"].get("request_timeout_seconds", 60))

    print("sample rows:", len(sample))
    print("selection fraction:", fraction)
    print("selection k:", k)
    print("model:", model)
    print("dry_run:", dry_run)
    print("batch_size:", batch_size)
    print("checkpoint enabled:", CHECKPOINT_ENABLED)
    print("resume from checkpoint:", RESUME_FROM_CHECKPOINT)
    print("checkpoint path:", CHECKPOINT_PATH)

    done = load_checkpoint()
    print("checkpoint loaded:", len(done))

    pending = sample[~sample["mutant_id"].isin(done.keys())].copy()
    print("pending:", len(pending))

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    client = None
    if not dry_run:
        load_dotenv(ROOT / ".env")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is missing. Copy .env.example to .env and paste your key.")

        from openai import OpenAI
        client = OpenAI(api_key=api_key)

    batch = []
    for _, row in tqdm(pending.iterrows(), total=len(pending), desc="Ranking mutants"):
        payload = make_mutant_payload(row)
        batch.append(payload)

        if len(batch) >= batch_size:
            if dry_run:
                ranked = [dry_run_score(x) for x in batch]
            else:
                ranked = call_openai_batch(
                    client, model, system_prompt, batch,
                    temperature, max_retries, timeout_seconds
                )
            append_checkpoint(ranked)
            done.update({x["mutant_id"]: x for x in ranked})
            if SAVE_EVERY_BATCH:
                save_current_outputs(sample, done, k)
            batch = []

    if batch:
        if dry_run:
            ranked = [dry_run_score(x) for x in batch]
        else:
            ranked = call_openai_batch(
                client, model, system_prompt, batch,
                temperature, max_retries, timeout_seconds
            )
        append_checkpoint(ranked)
        done.update({x["mutant_id"]: x for x in ranked})
        if SAVE_EVERY_BATCH:
            save_current_outputs(sample, done, k)

    llm_df = pd.DataFrame(done.values())
    llm_df["mutant_id"] = llm_df["mutant_id"].astype(str)

    merged = sample.merge(llm_df, on="mutant_id", how="inner")
    merged = normalize_rank_output(merged)

    merged.to_csv(LLM_OUTPUT_PATH, index=False)

    gpt_selected = merged.head(k).copy()
    gpt_selected.to_csv(GPT_SELECTED_PATH, index=False)

    print("Saved:", LLM_OUTPUT_PATH)
    print("Saved:", GPT_SELECTED_PATH)
    print("GPT selected:", len(gpt_selected))
    print("Checkpoint:", CHECKPOINT_PATH)
    print("Ranked total:", len(done))
    if len(done) < len(sample):
        print("WARNING: not all mutants are ranked yet. Rerun python scripts\\run_pipeline.py to resume.")
    else:
        print("All mutants ranked.")

    seeds = CONFIG["random"]["seeds"]
    with RANDOM_LOG_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["seed", "k", "output_path"])

        for seed in seeds:
            random_selected = sample.sample(n=k, random_state=int(seed)).copy()
            random_selected["random_seed"] = int(seed)
            out_path = RESULTS_DIR / f"full_random_selected_seed{seed}.csv"
            random_selected.to_csv(out_path, index=False)
            writer.writerow([seed, k, str(out_path)])

            print("Saved:", out_path)

    print("\nDONE")


if __name__ == "__main__":
    main()
