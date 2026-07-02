# LR Pipeline — GPT4o-mini Mutant Selection

This folder is for the LR role in the pilot experiment.

It prepares:

- GPT4o-mini mutant ranking
- top 10% GPT-selected mutants
- random fixed-seed baseline with `random_seed = 42`
- API log and cost log

## 1. Folder structure

```text
data/
  pilot_mutant_pool_template.csv
  sample_mutant_pool.csv
  pilot_mutant_pool.csv              # DG will provide this later

prompts/
  ranking_prompt.txt

scripts/
  validate_mutant_pool.py
  run_gpt_ranking.py
  random_baseline.py
  run_pipeline.py
  estimate_cost.py
  utils.py

results/
  pilot_gpt_ranking.csv
  pilot_gpt_selected.csv
  pilot_random_selected.csv

logs/
  validation_report.txt
  pilot_api_log.txt
  pilot_cost_log.csv
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Prepare API key

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Then edit `.env` locally:

```env
OPENAI_API_KEY=your_real_key_here
```

Do not commit `.env` to GitHub.

## 4. Test without API key

The default config has:

```yaml
dry_run: true
```

This allows the full pipeline to run using fake deterministic GPT scores.

```bash
python scripts/run_pipeline.py
```

Dry-run output is only for testing scripts, parser, CSV outputs, and logs.
Do not use dry-run output as research result.

## 5. Real pilot run

When DG sends the real file, put it here:

```text
data/pilot_mutant_pool.csv
```

Then edit `config.yaml`:

```yaml
dry_run: false
```

Run:

```bash
python scripts/run_pipeline.py
```

## 6. Expected outputs

After the pipeline runs, LR should hand over these files to MS:

```text
results/pilot_gpt_ranking.csv
results/pilot_gpt_selected.csv
results/pilot_random_selected.csv
logs/pilot_api_log.txt
logs/pilot_cost_log.csv
```

## 7. Required input columns

DG should provide `data/pilot_mutant_pool.csv` with at least:

```text
mutant_id
project
version
class_name
mutation_operator
original_code
mutated_code
surrounding_context
```

Recommended extra columns:

```text
method_name
line_number
```

## 8. Important rule

Do not change model, prompt, budget, or random seed during the pilot unless the team records an approved amendment.


## 9. Checkpoint / resume

Checkpoint file:

```text
results/pilot_gpt_checkpoint.jsonl
```

If API quota/billing/network error stops the run halfway:

1. Do not delete `results/pilot_gpt_checkpoint.jsonl`.
2. Top up credit or fix the issue.
3. Rerun:

```bash
python scripts/run_pipeline.py
```

The script will skip completed `mutant_id` values and call API only for pending mutants.

To intentionally rerun from zero, edit `config.yaml`:

```yaml
reset_checkpoint: true
```

Run once, then set it back to:

```yaml
reset_checkpoint: false
```
