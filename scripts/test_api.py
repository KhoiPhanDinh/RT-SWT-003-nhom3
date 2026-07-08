"""Gate E3 smoke test: 1 API call to confirm GPT4o-mini config works end to end.

Usage:
    python scripts/test_api.py

Requires OPENAI_API_KEY in .env (see utils.load_env). Does not touch any
checkpoint/results file used by the real pipeline.
"""
from __future__ import annotations

import os
import sys

from utils import load_config, load_env


SAMPLE_MUTANT = {
    "mutant_id": "TEST_0",
    "project": "Lang",
    "version": "1f",
    "class_name": "org.apache.commons.lang3.StringUtils",
    "method_name": "isEmpty",
    "line_number": 100,
    "mutation_operator": "NegateConditionalsMutator",
    "original_code": "if (str == null || str.length() == 0) { return true; }",
    "mutated_code": "if (str == null && str.length() == 0) { return true; }",
    "surrounding_context": "public static boolean isEmpty(CharSequence str) { ... }",
}


def main() -> int:
    cfg = load_config()
    load_env()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not found. Create .env with OPENAI_API_KEY=... first.")
        return 1

    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    prompt_path_text = (
        "You are given a list of Java mutants. Each mutant includes a mutant ID, "
        "mutation operator, original code, mutated code, and surrounding code context.\n\n"
        "Your task is to rank the mutants by usefulness for mutation testing.\n\n"
        "For each mutant, return: mutant_id, usefulness_score (1-5), short_reason.\n"
        "Return the final answer as a JSON array.\n\n"
        f"Mutants to rank:\n{[SAMPLE_MUTANT]}"
    )

    response = client.chat.completions.create(
        model=cfg["model"],
        temperature=float(cfg.get("temperature", 0)),
        top_p=float(cfg.get("top_p", 1)),
        messages=[
            {"role": "system", "content": "You are a careful mutation testing research assistant. Return valid JSON only."},
            {"role": "user", "content": prompt_path_text},
        ],
    )

    content = response.choices[0].message.content
    print("=== Gate E3: single API call test ===")
    print("model:", cfg["model"])
    print("usage:", response.usage)
    print("raw response:")
    print(content)
    print("\n[OK] API call succeeded. Gate E3 passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
