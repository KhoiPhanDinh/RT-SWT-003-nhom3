# Research Proposal: GPT4o-mini-based Mutant Selection for Java Mutation Testing

**Nhóm:** Nhóm 3

**Thành viên:** Phạm Mạnh Quỳnh (SE191021), Phan Nguyễn Đình Khôi (SE190954), Nguyễn Nhật Anh (SE192077), Nguyễn Trường Vinh (SE191072), Trần Trúc Vy (SE204433)

**Topic code:** [RT-SWT-00X]

**Ngày nộp:** [YYYY-MM-DD]

**Version:** 1.0

**Trạng thái:** Đang chờ phê duyệt

---

# 2. Research Problem Statement

## 2.1 Bối cảnh & Tầm quan trọng
Mutation testing là kỹ thuật đánh giá chất lượng test suite bằng cách tạo ra các mutant (biến thể lỗi nhỏ của chương trình) và kiểm tra khả năng test phát hiện chúng. Kỹ thuật này quan trọng với developer và QA engineer vì nó phát hiện những điểm yếu mà coverage thông thường bỏ sót.

Tuy nhiên, mutation testing gặp vấn đề lớn là số lượng mutant sinh ra rất lớn, dẫn đến chi phí thực thi cao và khó áp dụng trong thực tế. Các nghiên cứu như Cerebro (TSE 2023) và LEAM++ (Tian et al. 2025) đã cho thấy nhu cầu giảm số lượng mutant thông qua mutant selection nhằm cân bằng giữa chi phí và hiệu quả kiểm thử. Vì vậy, việc lựa chọn một tập con mutant hiệu quả là vấn đề quan trọng cả về nghiên cứu lẫn thực tiễn.

## 2.2 State of the Art
- **PRIMG (2025):** dùng LLM hỗ trợ test generation và mutant prioritization trong mutation testing, cho thấy tiềm năng của LLM.
- **Cerebro (TSE 2023):** áp dụng machine learning trên đặc trưng data flow / control flow để dự đoán subsuming mutants, chọn ra các mutant quan trọng.
- **LEAM++ (Tian et al. 2025):** học cách chọn/sinh selective mutation faults chất lượng cao để giảm số mutant cần dùng.
- **GPT4o-mini / LLM gần đây** được dùng cho mutant generation (Wang et al. 2025; SMART) và equivalent mutant detection (GEM-LLM), nhưng tập trung vào việc *sinh* hoặc *lọc* mutant, chưa phải *chọn* một subset để so với random.
- **Random selection** vẫn được dùng rộng rãi làm baseline do đơn giản và dễ tái lập.

## 2.3 GAP
**GAP-T** 

GPT4o-mini đã được dùng như một công cụ hỗ trợ trong mutation testing (đặc biệt cho mutant generation và equivalent mutant detection). Tuy nhiên, vai trò của GPT4o-mini như một bộ quyết định để chọn mutants hữu ích vẫn chưa được đánh giá đầy đủ so với random fixed-seed selection dưới cùng mutant budget.

## 2.4 Motivation
Nếu không đánh giá GPT4o-mini trong cùng điều kiện kiểm soát với random selection (cùng mutant budget, cùng metric), không thể xác định liệu việc dùng LLM có thực sự cải thiện hiệu quả mutation testing hay không. Hệ quả thực tế: khó ra quyết định áp dụng, và có nguy cơ tốn chi phí gọi API mà không thu được lợi ích rõ ràng so với một baseline đơn giản như random.

---

# 3. Related Work

## 3.1 Overview

| Paper | Tool/LLM | Dataset (size) | Metric | Best result / finding | Hạn chế chính liên quan đến GAP |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Wang et al. (2025) - *A Comprehensive Study on LLMs for Mutation Testing* | GPT4o-mini, GPT4o-mini-mini, GPT-3.5, DeepSeek, CodeLlama; baselines include PIT/Major/LEAM | Defects4J 2.0 + ConDefects; Java bugs | Real bug detection rate, compilability, duplicate rate, equivalent mutant rate, mutation score | LLM-based approaches improve real bug detection compared with rule-based mutation techniques | GPT4o-mini/LLM is used mainly for **mutant generation/evaluation**, not as a mutant selection decision-maker |
| Wang et al. (2026) - *SMART / Boosting LLMs for Mutation Generation* | SMART with RAG + focused code chunking + SFT; includes GPT4o-mini among evaluated LLMs | Defects4J + ConDefects; Java real-world bugs | Validity, non-duplicate rate, real bug detection rate, Ochiai | SMART improves validity and real bug detection over prior LLM mutation generation approaches | Focuses on **semantic mutant generation**, not selecting a reduced mutant subset versus random |
| Wang et al. (2026) - *MUTGEN* | Llama-3.3 70B; mutation-guided unit test generation | HumanEval-Java + LeetCode-Java | Mutation score, line/branch coverage | Reports high mutation score on Java programming benchmarks and outperforms EvoSuite/vanilla LLM prompting | Uses mutation testing to guide **test generation**, not to evaluate GPT4o-mini-selected mutant subsets |
| Tanhaei & Alizadehsani (2026) - *GEM-LLM* | GPT4o-mini + Gemma + SMT solver | Defects4J; Java; surviving/PIT mutants | Equivalent detection rate, precision | Identifies contextual equivalent mutants with high precision | GPT4o-mini is used for **equivalent mutant detection/filtering**, not mutant selection against random baseline |
| Zhao et al. (2024) - *SODA* | CodeT5-based mutational semantic learning with contrastive learning; Major | Six Defects4J v2.0.0 Java projects | kill-F1, survive-F1, accuracy, mutation score error | Improves kill/survive prediction and reports low mutation score error in cross-version/cross-project settings | Predicts mutant-test outcomes, but does not evaluate GPT4o-mini as a mutant selection method |
| Jain et al. (2023) - *MutationBERT* | Fine-tuned CodeBERT for mutant-test prediction; Major | Six Defects4J 2.0 Java projects; mutant-test pairs | Precision, recall, F1, mutation score error, time | Improves same-project and cross-project prediction over prior PMT baselines | Requires training/fine-tuning and focuses on prediction, not GPT4o-mini-based subset selection |
| Kim et al. (2022) - *Seshat* | DNN with natural language channel; PIT & Major | Defects4J v2.0.0; Java projects/versions | Precision, recall, F-score | Predicts kill matrix faster than running tests directly | PMT model depends on project naming/coding conventions and does not compare GPT4o-mini-selected subsets with random |
| Tian et al. (2025) - *LEAM++* | Learning-based selective mutation fault construction | Defects4J / Java projects | Mutation score, mutant reduction, downstream testing effectiveness | Shows selective/high-quality mutant construction can reduce mutants while supporting testing tasks | Relevant to mutant reduction, but not GPT4o-mini decision-making or random fixed-seed subset comparison |
| Jimenez et al. (2018) - *Mutant Naturalness* | N-gram language model; Major | Five Defects4J Java projects; >100k mutants | Fault revelation vs random, Wilcoxon test, A12 effect size | Naturalness-based selection is mostly close to random; paper provides a useful ranking-vs-random evaluation pattern | Uses n-gram naturalness, not GPT4o-mini; useful as the closest base pipeline for subset selection comparison |
| Bouafif et al. (2025) - *PRIMG* | Llama 3.1 8B + mutant prioritization module | Solidity smart contracts from Code4Arena | Mutation score, valid tests, test suite size | Mutant prioritization is reported to perform better than random selection in its own test-generation setting | Dataset/language is Solidity, and prioritization supports test generation rather than Java GPT4o-mini mutant selection |

## 3.2 Pattern Analysis
Từ các paper trên, có thể rút ra bốn pattern chính:

1. **LLM đã được dùng trong mutation testing, nhưng chủ yếu ở vai trò generation hoặc filtering.**  
   Các nghiên cứu như Wang et al. (2025), SMART và GEM-LLM cho thấy GPT4o-mini/LLM có thể hỗ trợ mutation testing thông qua mutant generation, semantic mutation generation hoặc equivalent mutant detection. Tuy nhiên, các nghiên cứu này chưa đánh giá GPT4o-mini như một **decision-maker** để chọn một subset mutants hữu ích so với random fixed-seed selection.

2. **Predictive Mutation Testing (PMT) dùng ML/DL để dự đoán killed/survived, nhưng khác với mutant selection bằng GPT4o-mini.**  
   SODA, MutationBERT và Seshat tập trung dự đoán mutant-test outcomes hoặc kill matrix bằng CodeT5, CodeBERT hoặc DNN. Các metric thường là F1, accuracy, mutation score error hoặc prediction time. Đây là hướng prediction, không phải thiết kế đánh giá trực tiếp `MS_GPT4o` so với `MS_random` dưới cùng mutant budget.

3. **Mutant reduction/selection là hướng nghiên cứu hợp lý, nhưng chưa có đánh giá trực tiếp cho GPT4o-mini.**  
   LEAM++ chứng minh hướng chọn/sinh mutants chất lượng cao có liên quan đến việc giảm số mutants. Jimenez et al. cung cấp pattern gần nhất cho pipeline: rank/chọn mutants theo một score và so với random cùng kích thước. Tuy nhiên, score trong Jimenez là n-gram naturalness, không phải GPT4o-mini usefulness judgment.

4. **Random baseline vẫn cần thiết để kiểm tra giá trị thực của phương pháp selection.**  
   Các paper như Jimenez et al. và PRIMG đều cho thấy random selection là baseline quan trọng. Vì vậy, nghiên cứu hiện tại giữ random fixed-seed selection làm baseline để kiểm tra xem GPT4o-mini có thật sự chọn subset mutants tốt hơn một phương pháp đơn giản và tái lập được hay không.

## 3.3 GAP Mapping

| Cột GAP (Loại) | Nội dung GAP | Evidence support | Status |
| :--- | :--- | :--- | :--- |
| **GAP-T** (Technology) | GPT4o-mini đã được dùng như một công cụ hỗ trợ trong mutation testing, nhưng vai trò của GPT4o-mini như một bộ quyết định để chọn mutants hữu ích vẫn chưa được đánh giá đầy đủ so với random fixed-seed selection dưới cùng mutant budget. | LLM/GPT4o-mini papers support prior use in generation/filtering: Wang et al. (2025), SMART, GEM-LLM. PMT/reduction papers show related but different directions: SODA, MutationBERT, Seshat, LEAM++. Random/ranking baseline is supported by Jimenez and PRIMG. | Confirmed |
| **GAP-M** (Metric) | Các paper hiện tại thường đo riêng prediction quality, mutant generation quality hoặc equivalent mutant detection quality, nhưng chưa đánh giá trực tiếp hiệu quả của subset mutants do GPT4o-mini chọn so với random fixed-seed selection dưới cùng mutant budget bằng mutation score. | PMT papers use F1/accuracy/MS error; LLM generation papers use validity, bug detection, compilability or equivalent rate; equivalent detection papers use precision/recall. These metrics do not directly answer whether `MS_GPT4o > MS_random`. | Confirmed |
| **GAP-D** (Dataset / Setting) | Java/Defects4J không phải GAP chính vì đã xuất hiện trong nhiều paper; nó được dùng làm setting public để kiểm tra GAP-T và GAP-M. | Defects4J/Java appears in SODA, MutationBERT, Seshat, LEAM/LEAM++, GEM-LLM, Wang et al. (2025), SMART and Jimenez et al. | Confirmed - Supporting setting |
| **GAP-R** (Reproducibility) | Cần mô tả rõ prompt, input features, model setting, selected mutant IDs, random seed, budget và cách tính mutation score để pipeline có thể tái lập. | Related LLM/PMT papers often report different configurations and metrics; the current study uses fixed prompt, fixed budget and random seed to improve reproducibility. | Confirmed - Supporting |

---

# 4. Research Questions

> **RQ1:** Trên **Defects4J Java projects** (P), liệu **GPT4o-mini-based mutant selection** — GPT4o-mini (`gpt-4o-mini`), fixed ranking prompt, temperature = 0 (I) — có đạt **mutation score cao hơn random fixed-seed selection khi cả hai chọn top 10% mutants** (O) so với **random fixed-seed selection cùng budget** (C) không?

**Loại claim:** Comparative (Case 2) — so sánh 2 hệ thống (GPT4o-mini selection vs random fixed-seed selection) dưới cùng mutant budget; không đặt ngưỡng tuyệt đối, chỉ cần MS_GPT4o > MS_random.

**H0:** GPT4o-mini-based mutant selection **KHÔNG tốt hơn** random fixed-seed selection về mutation score khi cả hai chọn top 10% mutants trên Defects4J Java projects (MS_GPT4o ≤ MS_random).

**H1:** GPT4o-mini-based mutant selection **tốt hơn** random fixed-seed selection về mutation score khi cả hai chọn top 10% mutants trên Defects4J Java projects (MS_GPT4o > MS_random).

**Metric:** Mutation score = Killed / Selected, đo bằng mutation testing tool **PIT (Pitest)** (chốt tại §5.3).

**Ngưỡng:** Comparative — MS_GPT4o > MS_random (không có ngưỡng tuyệt đối). Mutant budget = **top 10% mutant pool** — **budget source gần nhất: AL-PMT (Borsi 2025)** báo cáo đạt 98% best-possible performance ở hơn 80% projects khi chỉ observe 10% mutant kill status. NOTE: AL-PMT là active-learning predictive mutation testing (đo F1/ROC-AUC), không phải LLM-based selection; 10% được dùng làm budget nguồn gần nhất, không phải ngưỡng đã chứng minh cho LLM selection.

**Statistical test:** Wilcoxon signed-rank test (α = 0.05) — paired theo từng project/version/class. Nếu số cặp quá ít, báo cáo descriptive comparison trước (một phía; effect size báo cáo ở §5.6).

---

# 5. Experiment Protocol

## 5.1 Overview of Experimental Pipeline

This study investigates whether **GPT4o-mini-based mutant selection** achieves a higher mutation score than **random fixed-seed selection** under the same mutant budget.

The experiment follows a controlled comparative pipeline. Mutants are first generated from selected Java projects, then the same mutant pool is given to two selection strategies:

1. **GPT4o-mini-based mutant selection**
2. **Random fixed-seed mutant selection**

Both strategies select the same number of mutants, using the same fixed mutant budget. The selected mutants are then executed and compared using mutation score.

### Step 1 - Prepare dataset

1. Select a medium-size subset of Java projects from Defects4J, such as Commons Lang and Commons Math.
2. Checkout the selected project/version.
3. Build the project and run the original test suite.
4. Record successful project/version/class targets before mutation generation.

### Step 2 - Generate mutants

1. Use PIT to generate mutants for the selected project/version/class.
2. Save mutant information, including:
   - mutant ID;
   - project/version/class;
   - mutation operator;
   - original code;
   - mutated code;
   - surrounding code context.

### Step 3 - GPT4o-mini-based mutant selection

1. Prepare a fixed prompt template.
2. Provide GPT4o-mini with explicit mutant information, including mutation operator, original code, mutated code, and surrounding code context.
3. Ask GPT4o-mini to rank or score mutants by usefulness for mutation testing.
4. Select the top mutants according to the fixed mutant budget, such as 10% of the mutant pool.
5. Save the prompt, model version, model parameters, GPT4o-mini output, ranking result, and selected mutant IDs.

### Step 4 - Random fixed-seed baseline

1. Use the same mutant pool as GPT4o-mini.
2. Randomly select the same number of mutants as GPT4o-mini.
3. Use a fixed seed such as `random.seed(42)` for reproducibility.
4. If time allows, repeat random selection with several seeds and report the average result.

### Step 5 - Execute selected mutants

1. Run the test suite on GPT4o-mini-selected mutants.
2. Run the test suite on random-selected mutants.
3. Count killed and survived mutants for each selected subset.

### Step 6 - Compute mutation score

Mutation score is calculated as:

```text
Mutation Score = Killed Mutants / Selected Mutants
```

For each project/version/class, compute:

```text
MS_GPT4o = mutation score of GPT4o-mini-selected mutants
MS_random = mutation score of random fixed-seed selected mutants
```

### Step 7 - Compare results

Compare:

```text
MS_GPT4o vs MS_random
```

The main comparison checks whether GPT4o-mini-based mutant selection achieves a higher mutation score than random fixed-seed selection under the same mutant budget.

If there are enough paired cases, the study will use Wilcoxon signed-rank test. If the dataset is too small, the study will report descriptive comparison first.

---

## 5.2 Dataset

### Dataset Source

The experiment uses the Defects4J benchmark.

Repository:

```text
https://github.com/rjust/defects4j
```

Defects4J is selected because it is a public Java benchmark and appears in several mutation testing and predictive mutation testing studies. It supports reproducible experimentation and provides real-world Java projects with test suites.

### Selected Projects

The experiment focuses on a medium-size subset of Defects4J instead of the full benchmark.

Suggested projects:

- Commons Lang
- Commons Math

### Dataset Justification

Defects4J is selected because:

- it is publicly available;
- it contains real-world Java bugs;
- it includes validated test suites;
- it is commonly used in mutation testing research;
- it allows the experiment to remain reproducible.

### Preprocessing

For each selected project/version/class:

1. Checkout the project/version.
2. Compile the project.
3. Run the original test suite.
4. Keep only targets that build and test successfully.

---

## 5.3 LLM and Tool Configuration

### Large Language Model

Primary model:

```text
gpt-4o-mini
```

Backup model:

```text
gpt-4o-mini
```

The exact model snapshot is pinned instead of using `latest`, so the experiment is more reproducible and less affected by silent model updates.

### Prompting Strategy

The study uses a **fixed prompt-based ranking strategy**.

No fine-tuning process or project-specific training data is provided to the model. GPT4o-mini is used as a mutant selection decision-maker based on explicit mutant information.

### Prompt Template

The exact prompt must be finalized and saved before running the experiment.

Fixed prompt template:

```text
You are given a list of Java mutants. Each mutant includes a mutant ID, mutation operator, original code, mutated code, and surrounding code context.

Your task is to rank the mutants by usefulness for mutation testing.

A useful mutant is a mutant that is likely to reveal weaknesses in the test suite and is less likely to be trivial or equivalent.

For each mutant, return:
1. mutant_id
2. usefulness_score from 1 to 5
3. short_reason

Return the final answer as a table sorted from most useful to least useful.
```

### Model Parameters

```text
temperature = 0
top_p = default
max_tokens = default
```

Temperature is fixed at zero to reduce randomness and improve reproducibility.

The following information must be logged for every run:

- prompt text;
- model version;
- model parameters;
- input mutant IDs;
- GPT4o-mini output;
- selected mutant IDs;
- API cost if available.

### Mutation Testing Tool

The experiment uses:

```text
PIT (Pitest)
```

Official website:

```text
https://pitest.org
```

PIT is selected because:

- it is widely used for Java mutation testing;
- it integrates with Maven;
- it generates mutation reports;
- it is feasible for a student-scale experiment.

### Execution Environment

```text
Platform:   Kaggle Notebook
Runtime:    Python / Java (OpenJDK)
CPU:        2× Intel Xeon @ 2.00 GHz (4 cores)
RAM:        30 GB
GPU:        không sử dụng (thực nghiệm không cần GPU)
Disk:       ~70 GB ephemeral
```

Kaggle được chọn vì:

- miễn phí, không cần cấu hình máy cá nhân;
- hỗ trợ cài Java/Maven/PIT qua shell commands trong notebook;
- môi trường cố định, dễ tái lập (mỗi session cùng Docker image);
- có thể lưu output notebook làm artifact để reproduce.

Lưu ý: mỗi Kaggle session có thời gian tối đa 12 giờ. Nếu PIT chạy quá lâu trên toàn bộ project, nhóm sẽ chia nhỏ theo class/version và chạy nhiều session.

### Ground Truth

Killed/survived status of each mutant is determined by running the project test suite through PIT. Ground truth is automated and does not require human annotation.

---

## 5.4 Measurement

### Primary Metric

The primary metric is mutation score:

```text
Mutation Score = Killed Mutants / Selected Mutants
```

The two main values are:

```text
MS_GPT4o
MS_random
```

The experiment compares these two values under the same fixed mutant budget.

### Mutant Budget

Both GPT4o-mini selection and random fixed-seed selection select the same percentage of mutants, such as:

```text
Top 10% mutants
```

Because both strategies use the same budget, effort is controlled equally across the two arms. The experiment does not claim that the selected subset proves correctness of the whole codebase. It only compares whether GPT4o-mini selects a more effective subset than random selection under the same resource constraint.

---

## 5.5 Baseline

### Random Fixed-Seed Selection

The baseline is:

```text
Random fixed-seed mutant selection
```

### Random Seed

Primary seed:

```text
42
```

Optional validation seeds:

```text
123
2026
```

### Baseline Justification

Random fixed-seed selection is used because:

- it is simple;
- it is reproducible;
- it is a fair baseline for mutant selection;
- it selects from the same mutant pool as GPT4o-mini;
- it uses the same mutant budget as GPT4o-mini.

---

## 5.6 Statistical Analysis Plan

### Research Question

**RQ1:** Does GPT4o-mini-based mutant selection achieve a higher mutation score than random fixed-seed selection under the same mutant budget?

### Hypotheses

**H0:** GPT4o-mini-based mutant selection does not achieve a higher mutation score than random fixed-seed selection.

```text
MS_GPT4o <= MS_random
```

**H1:** GPT4o-mini-based mutant selection achieves a higher mutation score than random fixed-seed selection.

```text
MS_GPT4o > MS_random
```

### Statistical Test

```text
Wilcoxon signed-rank test
one-sided
alpha = 0.05
```

The test compares paired mutation score values per project/version/class.

If the number of paired cases is too small, descriptive comparison will be reported first.

### Effect Size

```text
Matched-pairs rank-biserial correlation (r_rb)
Ngưỡng ý nghĩa thực tế: r_rb ≥ 0.30 (medium effect, Cohen 1988)
```

**Nguồn ngưỡng:** Jimenez et al. (2018, ESEM) so sánh naturalness-based mutant selection với random selection trên 5 Defects4J Java projects (>100k mutants, 230 real faults, bao gồm Commons Lang và Commons Math). Họ báo cáo chỉ đạt small effect size (A₁₂ ≈ 0.57–0.58, Vargha & Delaney 2000) và kết luận rằng naturalness-based selection "similar (slightly worse)" so với random — small effect không có ý nghĩa thực tế cho mutant selection. Do đó, nghiên cứu này yêu cầu ít nhất medium effect size (r_rb ≥ 0.30) để claim cải thiện thực tế so với random.

---

## Success Criteria

Kết quả ủng hộ H1 (comparative, Case 2) nếu **cả hai** điều kiện được thỏa:

### SC1 — ý nghĩa thống kê

```text
p < 0.05  (Wilcoxon signed-rank, một phía)
```

### SC2 — ý nghĩa thực tế

```text
r_rb ≥ 0.30  (matched-pairs rank-biserial ≥ medium effect)
```

**Nguồn ngưỡng SC2:** Jimenez et al. (2018, ESEM) cho thấy small effect (A₁₂ ≈ 0.57–0.58) không đủ để claim mutant selection tốt hơn random trên Defects4J. Do đó, cần ít nhất medium effect (r_rb ≥ 0.30, Cohen 1988) để kết luận GPT4o-mini selection có ý nghĩa thực tế.

Nếu `p ≥ 0.05` hoặc `r_rb < 0.30` hoặc `MS_GPT4o ≤ MS_random`, không đủ bằng chứng rằng GPT4o-mini selection vượt random fixed-seed selection dưới budget đã đánh giá.

---

# 6. Evaluation Plan

## 6.1 Bảng tiêu chí đánh giá

| RQ | Metric | Ngưỡng | Test | H0 bị reject khi... | Kết quả âm tính có ý nghĩa? |
|---|---|---|---|---|---|
| RQ1 | Mutation Score = Killed / Selected, paired theo project/version/class | Comparative: `MS_GPT4o > MS_random`, cùng top 10% mutant budget; effect size r_rb ≥ 0.30 (medium, Cohen 1988) | Wilcoxon signed-rank test, một phía, α = 0.05; matched-pairs rank-biserial correlation | `p < 0.05` **và** `r_rb ≥ 0.30` **và** `median(MS_GPT4o - MS_random) > 0` | Có. Nếu không reject hoặc r_rb < 0.30, đây là bằng chứng rằng GPT4o-mini selection chưa vượt random fixed-seed ở mức có ý nghĩa thực tế (Jimenez et al. 2018: small effect A₁₂ ≈ 0.57 không đủ cho mutant selection). |

---

## 6.2 Diễn giải kết quả

Ba tình huống kết quả cho RQ1:

### Case 1 - Significant positive (ủng hộ H1)

Điều kiện:

```text
MS_GPT4o > MS_random  VÀ  p < 0.05  VÀ  r_rb ≥ 0.30
```

Diễn giải:

> Có bằng chứng thống kê cho thấy GPT4o-mini-based mutant selection đạt mutation score cao hơn random fixed-seed selection dưới cùng mutant budget, với effect size ≥ medium. Kết quả này ủng hộ H1; kết quả mạnh nhất.

### Case 2 - Statistically significant nhưng effect size nhỏ

Điều kiện:

```text
p < 0.05  nhưng  r_rb < 0.30
```

Diễn giải:

> Có sự khác biệt thống kê nhưng chưa đạt mức có ý nghĩa thực tế. Jimenez et al. (2018) cho thấy small effect (A₁₂ ≈ 0.57) không đủ để claim mutant selection tốt hơn random. Nhóm báo cáo descriptive comparison như mean/median mutation score và win/loss count; **không** kết luận H1.

### Case 3 - Positive trend, không có ý nghĩa thống kê

Điều kiện:

```text
MS_GPT4o > MS_random  nhưng  p >= 0.05
```

Diễn giải:

> GPT4o-mini có xu hướng chọn được subset mutants tốt hơn random, nhưng bằng chứng thống kê chưa đủ mạnh. Nhóm báo cáo descriptive comparison và quy về cỡ mẫu nhỏ; **không** kết luận H1.

### Case 4 - Negative / no effect

Điều kiện:

```text
MS_GPT4o <= MS_random
```

Diễn giải:

> Không đủ bằng chứng để nói GPT4o-mini-based mutant selection tốt hơn random fixed-seed selection dưới budget đã xét. Kết quả này vẫn có ý nghĩa vì nó chỉ ra giới hạn của GPT4o-mini fixed prompt-based mutant selection khi thiếu thông tin như coverage, assertion, equivalent mutant filtering hoặc actual test execution behavior.

---

## 6.3 Sub-group analysis

Sub-group analysis được định nghĩa trước khi chạy experiment để tránh HARKing.

Sub-group chính:

```text
Commons Lang vs Commons Math
```

Điều kiện:

```text
n_group = số paired unit chạy được trong mỗi project
```

Quy tắc:

```text
Nếu n_group >= 10:
    chạy Wilcoxon signed-rank test riêng cho project đó

Nếu n_group < 10:
    chỉ báo cáo descriptive comparison
    không chạy statistical test riêng cho project đó
```

Các descriptive statistics cần báo cáo:

- median mutation score;
- mean mutation score;
- win/loss count;
- number of paired cases;
- number of selected mutants;
- killed/survived mutants.

---

## 6.4 Negative result interpretation

Kết quả âm tính vẫn có giá trị nghiên cứu.

Nếu GPT4o-mini-based mutant selection không vượt random fixed-seed selection, các lý do có thể gồm:

- GPT4o-mini chỉ nhìn code context, không biết đầy đủ test suite behavior.
- Mutant usefulness phụ thuộc vào coverage, assertions và runtime behavior.
- Random selection có thể chọn được mutants hữu ích do may mắn.
- Một số mutants có thể là equivalent hoặc trivial.
- Dataset hoặc số paired cases có thể quá nhỏ.
- Prompt cố định có thể chưa cung cấp đủ thông tin cho GPT4o-mini.

Khi đó, kết luận nên viết:

```text
There is not enough evidence to say that GPT4o-mini-based mutant selection outperforms random fixed-seed selection under the evaluated budget.
```

Không được viết:

```text
GPT4o-mini is useless for mutation testing.
```

---

## 6.5 HARKing prevention

The metric, threshold, statistical test, and sub-group analysis must be defined before running the experiment.

Không được:

- đổi metric sau khi thấy kết quả;
- thêm RQ mới sau khi thấy kết quả;
- đổi statistical test để lấy p-value tốt hơn;
- thêm sub-group analysis mới sau khi thấy data;
- bỏ random baseline vì kết quả không đẹp.

Nếu có thay đổi bắt buộc do lỗi kỹ thuật, thay đổi đó phải được ghi rõ trong amendment hoặc limitation.

---

# 7. Threats to Validity

> Mỗi threat có mitigation tương ứng trong protocol §5 và evaluation plan §6. Mục tiêu của section này là nêu rõ rủi ro có thể ảnh hưởng đến kết quả và cách nhóm kiểm soát rủi ro đó.

---

## 7.1 Internal Validity

### Threat 1 - Model version drift

**Threat:** GPT4o-mini có thể thay đổi hành vi theo thời gian nếu dùng model `latest` hoặc model không được pin version, dẫn đến kết quả không ổn định giữa các lần chạy.

**Mitigation:** Nhóm pin model snapshot cố định `gpt-4o-mini`, đặt `temperature = 0`, và log toàn bộ prompt, response, model version, model parameters và selected mutant IDs như đã mô tả trong §5.3.

### Threat 2 - Unfair comparison between GPT4o-mini and random selection

**Threat:** So sánh có thể không công bằng nếu GPT4o-mini và random selection không dùng cùng mutant pool, cùng số lượng mutants, hoặc cùng mutant budget.

**Mitigation:** Cả hai phương pháp đều chọn từ cùng một mutant pool và cùng top 10% mutant budget. Random baseline dùng fixed seed `42` để có thể tái lập. Nếu thời gian cho phép, nhóm chạy thêm seed kiểm chứng như `123` và `2026` như đã mô tả trong §5.5.

### Threat 3 - Limited input information for GPT4o-mini

**Threat:** GPT4o-mini chỉ nhận mutation operator, original code, mutated code và surrounding code context. Model không có đầy đủ thông tin về test coverage, assertion behavior hoặc execution history, nên ranking có thể không phản ánh chính xác khả năng mutant bị test suite kill.

**Mitigation:** Nhóm giữ input features cố định cho mọi mutant, log prompt/response đầy đủ, và diễn giải kết quả như một pilot về GPT4o-mini-based mutant selection dựa trên code context. Các thông tin nâng cao như coverage, test names, historical kill data hoặc equivalent mutant filtering được ghi nhận là future work.

---

## 7.2 External Validity

### Threat 1 - Limited project scope

**Threat:** Thí nghiệm được downscope trên một số project/version/class trong Defects4J, ví dụ Commons Lang và Commons Math. Kết quả có thể không đại diện cho mọi Java project hoặc mọi domain phần mềm.

**Mitigation:** Nhóm dùng Defects4J vì đây là benchmark Java public và phổ biến trong mutation testing research. Kết luận chỉ được giới hạn trong phạm vi dataset và project đã chạy, không khái quát quá mức sang toàn bộ Java ecosystem hoặc các ngôn ngữ khác.

### Threat 2 - Tool-specific result

**Threat:** Kết quả có thể phụ thuộc vào mutation testing tool được dùng, ví dụ PIT. Các tool khác như Major có thể sinh mutant khác hoặc báo cáo killed/survived khác.

**Mitigation:** Nhóm ghi rõ tool, version/configuration và operator set được dùng trong §5.3. Kết quả được diễn giải trong phạm vi PIT-based mutation testing. Việc kiểm tra với tool khác được ghi nhận là future work.

---

## 7.3 Construct Validity

### Threat 1 - Mutation score may not fully represent test suite quality

**Threat:** Mutation score là proxy để đo effectiveness của selected mutant subset, nhưng nó không phản ánh toàn bộ chất lượng test suite hoặc tính đúng đắn của toàn bộ codebase.

**Mitigation:** Nhóm dùng mutation score vì nó trực tiếp đo số mutants bị killed trong selected subset và phù hợp với RQ1. Tuy nhiên, nhóm không claim rằng selected subset đảm bảo correctness của toàn bộ codebase. Kết quả chỉ dùng để so sánh GPT4o-mini-based selection với random fixed-seed selection dưới cùng budget.

### Threat 2 - Equivalent mutants may distort mutation score

**Threat:** Equivalent mutants có thể survived dù test suite tốt, làm mutation score bị thấp hơn thực tế. Ngoài ra, GPT4o-mini và random selection có thể chọn tỷ lệ equivalent mutants khác nhau.

**Mitigation:** Mutation score trên selected subset được dùng làm metric thống nhất cho cả hai nhánh và được đo bằng cùng PIT configuration. Nhóm sẽ báo cáo rõ killed/survived count và xem equivalent mutants là một limitation của pilot. Nếu có thời gian, nhóm có thể kiểm tra thủ công một sample surviving mutants hoặc ghi nhận equivalent mutant filtering như future work.

### Threat 3 - GPT4o-mini usefulness score may not match actual mutant usefulness

**Threat:** Điểm usefulness do GPT4o-mini đưa ra có thể chỉ phản ánh sự hợp lý bề mặt của code mutation, không nhất thiết tương ứng với khả năng mutant bị test suite kill.

**Mitigation:** GPT4o-mini score chỉ được dùng để rank/select mutants. Hiệu quả thật sự được xác nhận bằng execution result từ PIT và mutation score. Nhóm không dùng GPT4o-mini explanation như ground truth.

---

## 7.4 Conclusion Validity

### Threat 1 - Small sample size and low statistical power

**Threat:** Số paired unit như project/version/class có thể nhỏ, dẫn đến thiếu statistical power và làm p-value không ổn định.

**Mitigation:** Nhóm chạy trên nhiều paired unit nhất có thể trong phạm vi 4 tuần. Nếu có đủ paired cases, nhóm dùng Wilcoxon signed-rank test một phía với α = 0.05 như §6.1. Nếu số cặp quá ít, nhóm báo cáo descriptive comparison trước và không over-claim.

### Threat 2 - Random baseline variability

**Threat:** Một random seed duy nhất có thể chọn được subset quá tốt hoặc quá tệ do may mắn, làm kết quả so sánh bị lệch.

**Mitigation:** Random seed chính là `42` để reproducibility. Nếu thời gian cho phép, nhóm chạy thêm seed kiểm chứng như `123` và `2026`, sau đó báo cáo average hoặc sensitivity analysis. Nếu chỉ dùng một seed, nhóm ghi rõ đây là limitation.

### Threat 3 - Multiple comparisons in sub-group analysis

**Threat:** Nếu chạy nhiều sub-group analysis sau khi nhìn data, kết quả có thể bị HARKing hoặc tăng nguy cơ false positive.

**Mitigation:** Sub-group analysis được định nghĩa trước trong §6.3, ví dụ Commons Lang vs Commons Math. Nếu `n_group < 10`, nhóm chỉ báo cáo descriptive comparison và không chạy statistical test riêng cho project đó.

---

# 8. Timeline & Resources

## 8.0 Phân công vai trò

| Role | Thành viên | Trách nhiệm trong experiment |
|---|---|---|
| PL | Phạm Mạnh Quỳnh | Coordinate tiến độ, review tính nhất quán của proposal, kiểm tra deadline và xử lý blockers |
| DG | Nguyễn Nhật Anh | Chuẩn bị dataset, verify Defects4J/PIT, tạo mutant pool, lưu ground truth killed/survived |
| LR | Phan Nguyễn Đình Khôi | Setup GPT4o-mini API, viết prompt, chạy GPT4o-mini ranking, log prompt/response/API cost |
| MS | Nguyễn Trường Vinh | Tính mutation score, chạy Wilcoxon nếu đủ paired cases, tính effect size, diễn giải kết quả |
| RW | Trần Trúc Vy | Viết proposal, threats to validity, timeline/resources, format document và chuẩn bị slides |

> Quy tắc: LR và MS không nên gộp vào cùng một người, vì người chạy LLM không nên tự verify toàn bộ kết quả thống kê của chính mình.

---

## 8.1 Resource Inventory

| Tài nguyên | Trạng thái | Owner | Ghi chú |
|---|---|---|---|
| Dataset: Defects4J | ✅ | DG | Public benchmark; dự kiến dùng Commons Lang và Commons Math |
| Mutation testing tool: PIT | ✅ | DG | Free, dùng để generate mutants và lấy killed/survived |
| GPT4o-mini API key | ⚠️ | LR | Cần API key và kiểm soát chi phí |
| Compute | ✅ | DG + LR | Kaggle Notebook (2×Xeon, 30 GB RAM, miễn phí, session tối đa 12h); chia nhỏ theo class/version nếu PIT chạy lâu |
| Script random baseline | ✅ | MS | Python `random.seed(42)` |
| Script metric/stat | ✅ | MS | Python, SciPy Wilcoxon signed-rank test |
| Prompt template | ✅ | LR | Fixed prompt-based ranking strategy |
| Report template | ✅ | RW | Markdown proposal trong `team-synthesis/proposal.md` |

---

## 8.2 Chi phí ước tính

| Item | Số lượng | Đơn giá ước tính | Tổng |
|---|---:|---:|---:|
| GPT4o-mini API ranking | 500–2,000 mutants | khoảng $0.007 / mutant | khoảng $4–15 |
| Rerun / prompt testing buffer | — | — | khoảng $5–10 |
| Dataset/tool | Defects4J + PIT | $0 | $0 |
| Compute local | Laptop cá nhân / local Maven | $0 | $0 |

**Tổng dự kiến:** khoảng **$10–25** cho một pilot/dataset tầm trung.

Chi phí có thể giảm bằng cách:

- giới hạn code context gửi vào GPT4o-mini;
- batch nhiều mutants trong một prompt;
- yêu cầu output ngắn theo format cố định;
- lưu toàn bộ GPT4o-mini response để không phải gọi lại API.

---

## 8.3 Timeline chi tiết

> Timeline bắt đầu từ Tuần 5 vì nhóm đã hoàn thành RBL-2. RBL-3 không tạo file per-member riêng, mà tổng hợp thành một file nhóm `team-synthesis/proposal.md`. Giai đoạn này tập trung vào viết proposal, kiểm tra consistency giữa GAP/RQ/metric/pipeline, và chuẩn bị tài nguyên cho pilot experiment.

| Tuần | Hoạt động | Owner | Output cụ thể |
|---|---|---|---|
| Week 5 | Chốt GAP-T, GAP-M, RQ, H0/H1, metric, baseline và mutant budget | PL + MS | `SLR/gap-analysis.md`, `experiment/hypotheses-draft.md` |
| Week 5 | Viết proposal Sections §1–§4: Title, Problem Statement, Related Work, Research Questions | RW + DG + MS | Draft `team-synthesis/proposal.md` phần §1–§4 |
| Week 5 | Chuẩn bị Section §5: dataset, pipeline, GPT4o-mini config, PIT setup, random baseline | LR + DG + MS | Draft §5 Experiment Protocol |
| Week 5 | Chuẩn bị Section §6: evaluation plan, reject H0 condition, interpretation of positive/negative results | MS | Draft §6 Evaluation Plan |
| Week 5–6 | Viết Section §7–§8: threats to validity, timeline, resources, API cost, contingency plan | RW + PL + LR | Draft §7–§8 |
| Week 6 | Merge các section thành một proposal thống nhất, kiểm tra consistency giữa §2, §4, §5, §6 | PL + RW | `team-synthesis/proposal.md` complete draft |
| Week 6 | Verify tài nguyên trước khi nộp: Defects4J/PIT có thể setup, GPT4o-mini API có thể dùng, prompt template đã có | DG + LR | `dataset-notes.md`, `prompt-template.md`, API cost estimate |
| Week 6 | Review cuối: sửa format, kiểm tra citation, kiểm tra không dùng claim quá mạnh, không đổi RQ/metric sau khi chốt | PL + RW + MS | Final `team-synthesis/proposal.md` |
| Week 6 | Làm slide bảo vệ proposal | RW + PL | `presentation/slides_proposal_defense.pptx` |
| Week 7 | Pilot experiment nếu proposal được duyệt | DG + LR + MS | `pilot_mutant_pool.csv`, `pilot_llm_output.csv`, `pilot_analysis.ipynb` |
| Week 8 | Full experiment hoặc mở rộng pilot tùy kết quả Week 7 | DG + LR + MS | `full_llm_output.csv`, `full_analysis.ipynb`, result table |

---

## 8.4 Contingency Plan

| Rủi ro | Khi nào phát hiện | Cách xử lý |
|---|---|---|
| Defects4J hoặc PIT setup lỗi | Week 5–6 | Giảm scope còn 1 project hoặc chọn class/version build được |
| GPT4o-mini API lỗi hoặc quá tốn chi phí | Week 6–7 | Giảm số mutants, rút ngắn code context, batch nhiều mutants trong một prompt |
| Mutation testing chạy quá lâu | Week 6–8 | Giảm số versions/classes, chỉ chạy subset tầm trung |
| GPT4o-mini output không đúng format | Week 6 pilot | Sửa prompt template trước khi chạy full experiment |
| Không đủ paired cases cho Wilcoxon | Week 8 | Báo cáo descriptive comparison, không over-claim statistical significance |
| Kết quả GPT4o-mini không hơn random | Week 8 | Báo cáo negative result như finding hợp lệ và phân tích limitation |
| Thành viên trễ deadline | Mỗi tuần | PL nhắc sau 24h, nếu trễ 48h thì redistribute task |

---

## 8.5 Checkpoint per member

| Role | Week 5 | Week 6 | Week 7 | Week 8 |
|---|---|---|---|---|
| PL | Chốt scope, GAP/RQ consistency | Merge proposal, final review | Pilot meeting note, amendment nếu cần | Theo dõi full experiment và blockers |
| DG | Verify dataset/tool | Chuẩn bị `dataset-notes.md`, mutant info format | `pilot_mutant_pool.csv`, `pilot_ground_truth.csv` | `full_mutant_pool.csv`, `full_ground_truth.csv` |
| LR | Draft prompt + GPT4o-mini config | Test prompt/API trên sample nhỏ | `pilot_llm_output.csv`, API log | `full_llm_output.csv`, cost log |
| MS | Chốt metric, H0/H1, Wilcoxon plan | Chuẩn bị analysis script | `pilot_analysis.ipynb` | `full_analysis.ipynb`, result table |
| RW | Draft §1–§4 | Draft §7–§8, format proposal, slides | Update proposal nếu có amendment | Chuẩn bị figures/tables nếu cần |

---

## 8.6 Quy trình Amendment

Amendment chỉ được dùng khi có vấn đề kỹ thuật phát hiện trong pilot, không dùng để thay đổi giả thuyết sau khi thấy kết quả.

### Khi cần amendment

| Phát hiện từ pilot | Cần amendment? | Lý do |
|---|---|---|
| Prompt output sai format, không parse được | ✅ Có | Lỗi kỹ thuật cần sửa trước full run |
| Dataset/project không build được | ✅ Có | Cần đổi scope kỹ thuật |
| PIT chạy quá lâu trên project đã chọn | ✅ Có | Cần downscope version/class |
| p-value không đẹp | ❌ Không | Đây là kết quả, không phải lỗi kỹ thuật |
| GPT4o-mini không hơn random | ❌ Không | Đây là finding hợp lệ |
| Muốn đổi metric sau khi thấy data | ❌ Không | Vi phạm HARKing |

### Template amendment

```md
# Proposal Amendment [v1.0 -> v1.1]

**Nhóm:** Nhóm 3  
**Ngày:** [YYYY-MM-DD]  
**Phát hiện từ pilot:** [Mô tả vấn đề kỹ thuật]  

## Thay đổi đề xuất

| Mục | Proposal v1.0 | Đề xuất v1.1 | Lý do kỹ thuật |
|---|---|---|---|
| [Section] | [Nội dung cũ] | [Nội dung mới] | [Lý do] |

## Sections bị ảnh hưởng

- [ ] §4 Research Questions
- [ ] §5 Experiment Protocol
- [ ] §6 Evaluation Plan
- [ ] §8 Timeline & Resources

**Đính kèm:** `results/pilot_analysis.ipynb` hoặc log kỹ thuật liên quan  
**Xin phê duyệt GV:** [Approved / Not approved] — Ngày: [YYYY-MM-DD]
```