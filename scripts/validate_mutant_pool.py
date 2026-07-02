from __future__ import annotations

from datetime import datetime

from utils import (
    ensure_parent,
    get_input_file,
    load_config,
    read_mutant_pool,
    resolve_path,
    validate_mutant_pool,
)


def main() -> int:
    cfg = load_config()
    input_path = get_input_file(cfg)
    df = read_mutant_pool(input_path)
    errors = validate_mutant_pool(df)

    report_path = resolve_path(cfg.get("validation_log_file", "logs/validation_report.txt"))
    ensure_parent(report_path)

    lines = [
        f"Validation time: {datetime.now().isoformat(timespec='seconds')}",
        f"Input file: {input_path}",
        f"Total rows: {len(df)}",
        f"Total columns: {len(df.columns)}",
        f"Columns: {list(df.columns)}",
        "",
    ]

    if errors:
        lines.append("Status: INVALID")
        lines.append("Errors:")
        lines.extend([f"- {e}" for e in errors])
    else:
        lines.append("Status: VALID")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
