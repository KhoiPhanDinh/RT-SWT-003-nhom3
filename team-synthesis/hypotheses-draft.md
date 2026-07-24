# Hypotheses Draft — TEAM SYNTHESIS — Mutation Testing Enhancement with AI
Ngày: 2026-06-03
Evidence table merged: **N = 34 papers** sau khi gộp và loại trùng.

> **PICO đã chốt:** Trên Java projects trong **Defects4J** (P), **GPT-4o zero-shot mutant ranking/selection** ở temperature = 0 (I) — so với **random fixed-seed mutant selection** ở cùng mutant budget (C) — có giữ được **mutation adequacy/score**, giảm **effort thực thi**, ưu tiên **mutation operator** khác biệt và **generalize ổn định** giữa các project hay không (O).

## RQ1 — Effort reduction & mutation adequacy retention

### H0

GPT-4o zero-shot mutant ranking **không đạt** đồng thời hai điều kiện sau so với random fixed-seed mutant selection ở cùng mutant budget trên Defects4J:

- Số mutants cần thực thi giảm **≥ 20%**.
- Mutation adequacy score được duy trì trong khoảng **±10%** (mức hao hụt ≤ 10%) so với baseline.

### H1

GPT-4o zero-shot mutant ranking **đạt** đồng thời hai điều kiện sau so với random fixed-seed mutant selection ở cùng mutant budget trên Defects4J:

- Số mutants cần thực thi giảm **≥ 20%**.
- Mutation adequacy score được duy trì trong khoảng **±10%** (mức hao hụt ≤ 10%) so với baseline.

### Statistical test dự kiến

- **Wilcoxon signed-rank test** (α = 0.05) cho metric liên tục/paired:
  - số mutants cần thực thi giữa LLM-ranked selection và random fixed-seed baseline;
  - mutation adequacy score giữa LLM-ranked selection và random fixed-seed baseline.
- **Binomial exact test** (α = 0.05) cho biến nhị phân đạt/không đạt ngưỡng:
  - một project/version có đạt cả hai tiêu chí **≥20% reduction** và **≤10% loss** hay không.

## RQ2 — Mutation operator prioritization

### H0

Phân bố mutation operators được LLM-based mutant ranking ưu tiên **không khác biệt đáng kể** so với random fixed-seed mutant selection.

### H1

Phân bố mutation operators được LLM-based mutant ranking ưu tiên **khác biệt đáng kể** so với random fixed-seed mutant selection.

### Statistical test dự kiến

- **Chi-square test of independence** nếu số lượng mutants trong từng nhóm operator đủ lớn.
- **Fisher's exact test** nếu một số nhóm operator có số lượng nhỏ.
- Nếu operator categories quá nhỏ/lẻ, gộp theo nhóm chính như arithmetic, relational, logical, statement deletion trước khi kiểm định.

## RQ3 — Generalization across projects

### H0

LLM-based mutant ranking **không generalize ổn định** giữa các Java projects trong Defects4J; hiệu quả reduction/effectiveness thay đổi đáng kể giữa các project groups.

### H1

LLM-based mutant ranking **generalize tương đối ổn định** giữa các Java projects trong Defects4J; hiệu quả reduction/effectiveness không suy giảm đáng kể giữa các project groups.

### Statistical test dự kiến

- **Mann–Whitney U test** nếu so sánh hai nhóm project độc lập.
- **Wilcoxon signed-rank test** nếu dữ liệu được ghép cặp theo cùng budget/seed/project-version.

