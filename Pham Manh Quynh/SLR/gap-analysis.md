# Gap Analysis - GPT-4o-based Mutant Selection for Mutation Testing

Evidence table: **Team evidence set after duplicate removal**  
Scope: **personal gap-analysis based on the team paper set**  
Date: 2026-06-11

> Nguyên tắc dùng trong file này: GAP được phát biểu dựa trên các hướng đã xuất hiện trong paper tổng hợp của nhóm. Không dùng câu quá mạnh như “chưa ai từng làm”. Thay vào đó, GAP tập trung vào việc **chưa được đánh giá đầy đủ** trong setting cụ thể của nhóm: GPT-4o-based mutant selection so với random fixed-seed selection dưới cùng mutant budget.

---

## Bảng GAP

| Cột | Phát hiện | Loại GAP | Phản chứng / kiểm tra từng nhóm paper |
|---|---|---|---|
| Tool / GPT-4o | GPT-4o đã được dùng như một công cụ hỗ trợ trong mutation testing, ví dụ trong các hướng mutant generation hoặc equivalent mutant detection. Tuy nhiên, vai trò của GPT-4o như một bộ quyết định để chọn mutants hữu ích vẫn chưa được đánh giá đầy đủ so với random fixed-seed selection dưới cùng mutant budget. | **GAP-T** | Các paper dùng GPT-4o/LLM thường tập trung vào mutant generation, semantic mutation generation, equivalent mutant detection hoặc mutation-guided test generation. Các paper predictive mutation testing dùng ML/DL như Random Forest, LightGBM, CodeBERT/MutationBERT hoặc contrastive learning để dự đoán killed/survived mutants, nhưng không đánh giá GPT-4o như một phương pháp chọn mutants so với random fixed-seed selection. |
| Metric | Các paper hiện tại thường đo riêng prediction quality, mutant generation quality hoặc equivalent mutant detection quality, nhưng chưa đánh giá trực tiếp hiệu quả của subset mutants do GPT-4o chọn so với random fixed-seed selection dưới cùng mutant budget bằng mutation score. | **GAP-M** | PMT papers thường dùng F1, AUC, accuracy, mutation score error hoặc prediction time. LLM mutant generation papers thường đo validity, compilability, duplicate rate, equivalent mutant rate, bug detection hoặc mutation-related quality. Equivalent mutant detection papers thường đo precision/recall hoặc detection quality. Các metric này liên quan nhưng chưa trực tiếp trả lời câu hỏi: subset mutants do GPT-4o chọn có mutation score cao hơn subset random cùng kích thước không? |
| Dataset | Java/Defects4J đã xuất hiện trong nhiều paper mutation testing và predictive mutation testing, nên thiếu dataset Java không phải GAP chính. Dataset chỉ là setting để kiểm tra GAP-T và GAP-M trong môi trường tái lập được. | GAP-D phụ | Nhiều paper đã dùng Java projects, Defects4J hoặc các benchmark tương tự. Vì vậy nhóm không claim “thiếu Java dataset”, mà chọn Java/Defects4J để đảm bảo experiment có public benchmark và dễ đối chiếu với prior work. |
| Reproducibility | Một số hướng LLM-based hoặc AI-based mutation testing có thể tích hợp nhiều thành phần nhưng không phải lúc nào cũng public đầy đủ prompt, input features, model setting, selected mutants, random seed, budget và cách tính metric. | GAP-R phụ | Nếu pipeline không mô tả rõ LLM nhận input gì, chọn mutant như thế nào, dùng budget bao nhiêu và so với baseline nào, thì khó tái lập hoặc so sánh công bằng. Vì vậy nhóm cần thiết kế pipeline minh bạch với prompt/features, fixed random seed, selected mutant IDs và mutation score calculation. |
| Limitation / Risk | Chọn mutants bằng GPT-4o có rủi ro vì độ hữu ích của mutant không chỉ phụ thuộc vào code context, mà còn phụ thuộc vào test coverage, assertions, equivalent mutants và actual test execution behavior. | GAP-S phụ | Đây là lý do experiment không nên giả định GPT-4o chắc chắn tốt hơn random. Nghiên cứu chỉ kiểm tra thực nghiệm xem GPT-4o-based selection có mang lại lợi ích dưới cùng mutant budget hay không. |

---

## Kiểm tra phản chứng cho GAP chính

GAP tuyên bố:

> **GPT-4o đã được dùng như một công cụ hỗ trợ trong mutation testing, nhưng vai trò của GPT-4o như một bộ quyết định để chọn mutants hữu ích vẫn chưa được đánh giá đầy đủ so với random fixed-seed selection dưới cùng mutant budget.**

| Nhóm paper | Đã lấp GAP chưa? | Chi tiết |
|---|---:|---|
| GPT-4o / LLM-based mutant generation | Không | Các paper nhóm này dùng GPT-4o hoặc LLM để sinh mutants hoặc cải thiện chất lượng mutants. Tuy nhiên mục tiêu chính là mutant generation, không phải chọn một subset mutants bằng GPT-4o để so với random fixed-seed selection. |
| SMART / semantic mutation generation | Không | SMART dùng RAG/SFT và LLM để cải thiện semantic mutation generation. Đây là hướng tạo mutants tốt hơn, không phải đánh giá GPT-4o như decision-maker để chọn mutants hữu ích dưới budget cố định. |
| GPT-4o / LLM-based equivalent mutant detection | Không | GEM-LLM và các paper tương tự dùng GPT-4o/LLM để phát hiện equivalent mutants hoặc hỗ trợ reasoning về equivalence. Đây là mutant quality filtering/detection, không phải mutant selection so với random baseline bằng mutation score. |
| LLM-based test generation / mutation-guided test generation | Không | Các paper như MUTGEN, PRIMG hoặc Meta/Foster dùng mutation testing để hướng dẫn hoặc đánh giá test generation. Outcome chính là chất lượng test suite hoặc test generation effectiveness, không phải mutation score của subset mutants do GPT-4o chọn. |
| Predictive mutation testing bằng ML/DL | Gần nhưng chưa đủ | SODA, WITNESS, MutationBERT, Seshat hoặc các paper PMT dùng mô hình như Random Forest, LightGBM, CodeBERT/MutationBERT hoặc contrastive learning để dự đoán killed/survived mutants. Tuy nhiên chúng không đánh giá GPT-4o-based mutant selection so với random fixed-seed selection. |
| Mutant reduction / selective mutation | Gần nhưng chưa đủ | LEAM/LEAM++, mutant reduction, naturalness hoặc mutant selection papers chứng minh việc giảm số mutants là hướng hợp lý. Tuy nhiên các hướng này không trực tiếp kiểm tra GPT-4o chọn subset mutants bằng mutation score dưới cùng budget. |
| Random sampling / baseline-related papers | Hỗ trợ baseline nhưng chưa lấp GAP | Một số paper có dùng random như baseline hoặc so sánh với random. Tuy nhiên chúng không trả lời câu hỏi GPT-4o-selected mutants có hiệu quả hơn random fixed-seed selected mutants hay không. |

**Kết luận phản chứng:**  
Có nhiều paper gần với hướng này như LLM-based mutant generation, equivalent mutant detection, predictive mutation testing và mutant reduction. Tuy nhiên, chưa có bằng chứng đầy đủ trong team evidence set cho việc đánh giá **GPT-4o như một mutant selection method** so với **random fixed-seed selection** dưới cùng **mutant budget**, với **mutation score** làm metric chính.

---

## GAP chính

**GAP-T:** GPT-4o đã được dùng như một công cụ hỗ trợ trong mutation testing, nhưng vai trò của GPT-4o như một bộ quyết định để chọn mutants hữu ích vẫn chưa được đánh giá đầy đủ so với random fixed-seed selection dưới cùng mutant budget.

---

## GAP secondary

**GAP-M:** Các paper hiện tại thường đo riêng prediction quality, mutant generation quality hoặc equivalent mutant detection quality, nhưng chưa đánh giá trực tiếp hiệu quả của subset mutants do GPT-4o chọn so với random fixed-seed selection dưới cùng mutant budget bằng mutation score.

---

## Feasibility Check - GAP Chính

| Tiêu chí | Mức | Ghi chú |
|---|---|---|
| Dataset | ✅ An toàn | Dùng Java/Defects4J hoặc một phần nhỏ của benchmark public. Nhóm chỉ downscope vào một project hoặc một số classes/versions chạy được, không chạy toàn bộ benchmark. |
| Tool/API | ⚠️ Cần xử lý | Mutation testing tool như PIT/Major có thể dùng miễn phí, nhưng GPT-4o cần API và có thể tốn phí. Mitigation: giới hạn số mutants cần rank và lưu prompt/response. |
| Compute | ⚠️ Cần xử lý | Mutation testing có thể lâu nếu chạy full. Mitigation: chạy mini-pilot, dùng fixed mutant budget và chỉ chạy subset mutants đã chọn. |
| Ground truth | ✅ An toàn | Ground truth lấy từ kết quả mutation testing: killed/survived mutants. Không cần human annotation. |
| Skills | ✅ An toàn | Có thể triển khai bằng Java mutation testing tool + script Python để random fixed-seed selection, tính mutation score và so sánh kết quả. |
| Thời gian | ✅ An toàn | Khả thi nếu downscope nhỏ: một project, một số version/classes và số mutants giới hạn. |
| Contribution | ✅ An toàn | Đóng góp rõ: kiểm tra thực nghiệm vai trò của GPT-4o như một mutant selection method, với baseline và metric được xác định rõ. |

**Kết quả:** 5 ✅ / 2 ⚠️ / 0 ❌  
**Quyết định feasibility:** GAP này khả thi sau khi downscope. Nhóm không claim đánh giá toàn bộ codebase, mà chỉ so sánh GPT-4o-based selection với random fixed-seed selection trong một controlled pilot setting.

---

## Dataset selected for experiment

For the experiment, the group can use:

- **Dataset:** Defects4J or selected Java projects from the team evidence set.
- **Language:** Java.
- **Mutation testing tool:** PIT or Major, depending on setup feasibility.
- **Suggested scope:** one project or a small number of project versions/classes.
- **Reason:** Java/Defects4J appears in several mutation testing and PMT studies, and it allows the group to run mutation testing in a reproducible setting.

---

## Experiment Pipeline

### Step 1 - Prepare dataset

1. Select a small Java benchmark project or selected Defects4J project/version.
2. Build the project and run the original test suite.
3. Record successful project/version/class targets.

### Step 2 - Generate mutants

1. Use PIT or Major to generate mutants.
2. Save mutant information:
   - mutant ID;
   - project/version/class;
   - mutation operator;
   - original code;
   - mutated code;
   - surrounding code context.

### Step 3 - GPT-4o-based mutant selection

1. Prepare a fixed prompt template.
2. Provide GPT-4o with explicit mutant information, such as mutation operator, original code, mutated code and code context.
3. Ask GPT-4o to rank or score mutants by usefulness for mutation testing.
4. Select the top mutants according to a fixed budget, for example 10% of the mutant pool.
5. Save the prompt, model setting, GPT-4o output and selected mutant IDs.

### Step 4 - Random fixed-seed baseline

1. Use the same mutant pool as GPT-4o.
2. Randomly select the same number of mutants.
3. Use a fixed seed such as `random.seed(42)` for reproducibility.
4. If time allows, repeat random selection with several seeds and report the average.

### Step 5 - Execute selected mutants

1. Run the test suite on GPT-4o-selected mutants.
2. Run the test suite on random-selected mutants.
3. Count killed and survived mutants.

### Step 6 - Compute mutation score

Mutation score is calculated as:

```text
Mutation Score = Killed Mutants / Selected Mutants
```

For each project/version/class, compute:

```text
MS_GPT4o = mutation score of GPT-4o-selected mutants
MS_random = mutation score of random fixed-seed selected mutants
```

### Step 7 - Compare results

Compare:

```text
MS_GPT4o vs MS_random
```

Main question:

> Under the same mutant budget, does GPT-4o select a mutant subset with higher mutation score than random fixed-seed selection?

If there are enough paired cases, use Wilcoxon signed-rank test. If the dataset is too small, report descriptive comparison first.

---

## Final result evaluation

The result is evaluated by comparing **GPT-4o-based mutant selection** with **random fixed-seed selection** under the same **mutant budget**.

### Success case

The experiment is considered successful if:

```text
MS_GPT4o > MS_random
```

If there are enough paired cases, the result is stronger when:

```text
p-value < 0.05
```

using Wilcoxon signed-rank test.

### Not successful case

The experiment is not considered successful if:

```text
MS_GPT4o <= MS_random
```

or if the statistical test gives:

```text
p-value >= 0.05
```

In this case, the group should conclude:

> There is not enough evidence to say that GPT-4o-based mutant selection is better than random fixed-seed selection under the evaluated budget.

### Possible reasons if the result is not successful

- GPT-4o may not have enough information about the test suite.
- Code context alone may not reveal whether a mutant will be killed.
- Random selection can sometimes choose useful mutants by chance.
- Some useful mutants depend on coverage, assertions, or runtime behavior.
- The sample size may be too small.

### Lesson learned

Even if GPT-4o does not outperform random fixed-seed selection, the study is still useful because it provides evidence about whether GPT-4o can act as a mutant selection decision-maker under a fixed budget. A negative result can suggest that future work should include richer information such as test coverage, test names, historical kill data, equivalent mutant filtering, or few-shot examples.

---

## Phát biểu GAP 1-2 câu dùng trong proposal

GPT-4o has been used as a support tool in mutation testing, especially for tasks such as mutant generation and equivalent mutant detection. However, its role as a decision-maker for selecting useful mutants has not been sufficiently evaluated against random fixed-seed selection under the same mutant budget. This study addresses that gap by comparing the mutation score of GPT-4o-selected mutant subsets with random-selected subsets in a small-scale Java mutation testing setting.

---

## Ghi chú về phạm vi claim

This study does not claim that GPT-4o-based mutant selection has never been attempted. It only claims that the available evidence does not sufficiently evaluate GPT-4o as a mutant selection method against random fixed-seed selection under the same budget using mutation score.

The selected mutant subset is used as a cost-reduced evaluation proxy, not as proof of full correctness of the whole codebase.
