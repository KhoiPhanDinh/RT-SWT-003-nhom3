# LR Full Pipeline: Codec + Csv + JacksonCore

Dataset target:
- Codec 1f-10f
- Csv 1f-10f
- JacksonCore 1f-10f

Expected input files:
- `data/full_sample.csv`
- `data/full_ground_truth.csv`

This package already includes `data/full_sample.csv`. Copy `full_ground_truth.csv` from Kaggle into `data/` before metric computation.

## Checkpoint đã được bật

Trong `config.yaml`:

```yaml
checkpoint:
  enabled: true
  resume: true
  path: logs/full_gpt_checkpoint.jsonl
  save_every_batch: true
  api_log_path: logs/full_api_log.csv
```

Ý nghĩa:
- Sau mỗi batch API thành công, kết quả được ghi ngay vào `logs/full_gpt_checkpoint.jsonl`.
- Nếu mất mạng, hết token, laptop tắt, hoặc CMD bị đóng, chỉ cần chạy lại cùng lệnh.
- Script sẽ đọc checkpoint và bỏ qua các mutant đã rank.
- `results/full_llm_output.csv` và `results/full_gpt_selected.csv` cũng được lưu sau mỗi batch khi `save_every_batch: true`.

## Setup trên Windows CMD

```cmd
cd /d D:\Khoi\Semester_5_SU26\SWR\LR_FULL
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Mở `.env` và dán API key.

## Kiểm tra data

```cmd
python scripts\check_full_data.py
```

## Chạy thử không tốn tiền

Giữ `dry_run: true` trong `config.yaml`, rồi chạy:

```cmd
python scripts\run_pipeline.py
```

## Chạy thật GPT-4o-mini

Sửa `config.yaml`:

```yaml
dry_run: false
```

Chạy:

```cmd
python scripts\run_pipeline.py
```

Nếu bị dừng giữa chừng, chạy lại đúng lệnh đó:

```cmd
python scripts\run_pipeline.py
```

Không xóa file này nếu muốn resume:

```text
logs/full_gpt_checkpoint.jsonl
```

## Tính metric

Sau khi copy `full_ground_truth.csv` vào `data/`, chạy:

```cmd
python scripts\compute_metric_full.py
```

## Output chính

- `results/full_llm_output.csv`
- `results/full_gpt_selected.csv`
- `results/full_random_selected_seed42.csv`
- `results/full_random_selected_seed123.csv`
- `results/full_random_selected_seed2026.csv`
- `results/full_selection_summary.csv`
- `results/full_project_version_scores.csv`
- `results/full_paired_mutation_scores.csv`
- `results/full_statistical_summary.csv`
- `logs/full_gpt_checkpoint.jsonl`
- `logs/full_api_log.csv`
- `logs/full_random_log.csv`
