# Research Question Final — LLM-Based Mutant Ranking for Mutation Testing

Evidence table merged: **N = 26 papers** after duplicate removal.

## RQ nhóm chính thức

Đối với **Java projects trong Defects4J sử dụng mutation testing** (P), liệu **LLM-based mutant ranking bằng GPT-4o với zero-shot ranking prompt và temperature = 0** (I) có thể **giảm số mutants cần thực thi ít nhất 30% trong khi vẫn duy trì mutation adequacy score trong khoảng ±10% so với random fixed-seed mutant selection baseline** (O), khi so sánh với **random mutant selection fixed seed** (C) không?

## PICO

- **P (Population):** Java projects trong Defects4J có source code, test suite và mutants để chạy mutation testing.
- **I (Intervention):** LLM-based mutant ranking bằng GPT-4o, zero-shot ranking prompt, temperature = 0.
- **C (Comparison):** Random mutant selection với fixed seed, cùng budget/số lượng mutants được chọn.
- **O (Outcome):**
  - **Effort reduction:** số mutants cần thực thi giảm **≥30%** so với baseline/full mutant set.
  - **Effectiveness retention:** mutation adequacy score được duy trì trong khoảng **±10%** so với random fixed-seed baseline.

## Cụ thể hóa theo evidence table nhóm

- Evidence table cho thấy nhiều nghiên cứu đã dùng AI/ML/LLM cho mutant generation, predictive mutation testing, equivalent mutant detection và mutation-guided test generation, nhưng chưa trực tiếp đánh giá **LLM-based mutant ranking/selection** so với **random fixed-seed mutant selection** trên Java mutation testing.
- Một số paper có liên quan đến giảm chi phí hoặc chọn mutant, ví dụ AL-PMT quan sát 10% mutant kill status, LEAM++ báo cáo 17.50% mutant reduction, và các nghiên cứu commit-relevant/subsuming mutants cho thấy mutant selection có thể giảm đáng kể số mutants cần xử lý. Tuy nhiên, evidence table không cung cấp một ngưỡng chuẩn chung cho LLM-based ranking.
- Vì vậy, ngưỡng **≥30% effort reduction** và **±10% mutation adequacy retention** được dùng như **experimental thresholds của nhóm**, không viết là ngưỡng đã được chứng minh chung trong literature.
