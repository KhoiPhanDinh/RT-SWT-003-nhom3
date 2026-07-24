# GAP Analysis — Mutation Testing Enhancement with AI
Evidence table: N = 10 paper | Ngày: 2026-06-07

## Bảng GAP (4 loại)
| Cột nguồn | Phát hiện | Loại GAP | Phản chứng (quét 10 paper) |
|---|---|---|---|
| Tool/LLM | Không paper nào dùng LLM frontier (GPT-4o, temperature=0) để TRỰC TIẾP chọn/giảm tập mutant | **GAP-T (chính)** | ✅ 10/10 paper không phản chứng |
| Metric/Kết quả | Rất ít paper so TRỰC TIẾP mutation score của tập mutant do AI chọn với random ở CÙNG số lượng | GAP-M | ⚠️ #3,#10 có so với random nhưng bằng n-gram/XGBoost, không phải LLM |
| Dataset | Chưa có nghiên cứu chọn-mutant-bằng-LLM trên Defects4J (benchmark Java chuẩn) | **GAP-D (secondary)** | ✅ |
| Hạn chế tự nêu | ≥ ceil(0.4×10)=4 paper thừa nhận chỉ đánh giá trên Java/Defects4J, khó tổng quát | GAP-S | ✅ #2,#4,#5,#7,#8 |

## GAP CHÍNH
### GAP-T (Technology) - Chính
**Bằng chứng (Cột Tool/Kỹ thuật):** Chỉ #2 (EMD) và #1 (sinh test) có dùng LLM. KHÔNG paper nào dùng LLM frontier (vd GPT-4o, temperature=0) để TRỰC TIẾP chọn/giảm tập mutant. Việc chọn/dự đoán mutant đều dùng ML/DL cổ điển: n-gram (#3), seq2seq (#7,#4), BERT (#9), graph features (#10), contrastive (#5).

### GAP-M (Metric)
**Bằng chứng (Cột Metric / Kết quả):** Đa số đo CHẤT LƯỢNG DỰ ĐOÁN (F1/F-score: #8=0.83, #2=+35.69%, #5 kill-F1, #9 F1). Rất ít paper so trực tiếp mutation score của tập mutant do AI chọn với random ở CÙNG số lượng. Chi phí chỉ báo cáo dạng tốc độ tương đối (#8 nhanh 39×) hoặc tiềm năng giảm (#6 tới 93%).

### GAP-D (Dataset)
**Bằng chứng (Cột Dataset):** Java/Defects4J phổ biến cho dự đoán (#4,#7,#8,#2,#5,#9) nhưng các so-sánh-với-random mạnh nhất lại ở C/Coreutils (#10) hoặc Solidity (#1). Chưa có nghiên cứu chọn-mutant-bằng-LLM trên benchmark Java chuẩn (Defects4J).

### GAP-S (Shared limitation)
**Bằng chứng (Cột Hạn chế tự nêu):** Hạn chế chung ≥ 4 paper cùng thừa nhận — chỉ đánh giá trên Java/Defects4J nên khó tổng quát ngôn ngữ khác: #2 (§5.3 External), #4 (§6.4 External), #7 (§6.3 External), #8 (§6 chọn ngôn ngữ/subject), và #5 (§7 chỉ 6 dự án Defects4J). Ưu tiên thấp nhất (GAP-T > GAP-M > GAP-D > GAP-S).

## Chi tiết kiểm tra phản chứng
**GAP tuyên bố:** "Không paper nào dùng LLM frontier (GPT-4o, temperature=0) TRỰC TIẾP chọn/giảm tập mutant."

| # | Paper | Kỹ thuật xử lý mutant (cột Tool/LLM) | Có làm GAP? | Ghi chú |
|---|---|---|---|---|
| 1 | Bouafif (PRIMG) | LLaMA 3.1 sinh/refine test + ML regression cho subsumption | Không | LLM dùng SINH TEST, không chọn mutant |
| 2 | Tian (LLM-EMD) | LLM fine-tuned embedding (UniXCoder) | Không | Chỉ PHÁT HIỆN equivalent mutant, không chọn để giảm |
| 3 | Jimenez | n-gram (Modified Kneser-Ney) | Không | ML cổ điển |
| 4 | Tian (LEAM++) | DL TreeGen + selective mutation | Không | DL chuyên dụng, không phải LLM frontier |
| 5 | Zhao (SODA) | CodeT5 + contrastive learning | Không | DL, không phải LLM frontier |
| 6 | Ojdanic | HOM observational slicing (PiTest) | Không | Không dùng LLM |
| 7 | Tian (LEAM) | DL TreeGen | Không | DL chuyên dụng |
| 8 | Kim (Seshat) | DNN GRU + attention | Không | Không phải LLM frontier |
| 9 | Jain (MutationBERT) | CodeBERT fine-tune dự đoán kill | Không | BERT nhỏ, không phải LLM frontier; dự đoán kill chứ không chọn để giảm |
| 10 | Ma (MuDelta) | XGBoost trên graph features | Không | ML cổ điển |

**Kết quả:** 0/10 paper phản chứng → GAP-T được xác nhận.

## Feasibility Check — GAP Chính
| Tiêu chí | Mức | Ghi chú |
|---|---|---|
| Dataset | ✅ An toàn | Defects4J public, free |
| Tool/API | ⚠️ Cần xử lý | PIT/Major free (Java); GPT-4o cần API key + tốn phí |
| Compute | ⚠️ Cần xử lý | Chạy FULL mutation để lấy MS_full khá nặng → giới hạn ≥3 dự án nhỏ |
| Ground truth | ✅ An toàn | MS_full deterministic = ground truth |
| Skills | ⚠️ Cần xử lý | Cần Java + cấu hình PIT/Major + script gọi API |
| Thời gian | ⚠️ Cần xử lý | FULL mutation + LLM calls — sát buffer, cần downscope |
| Contribution | ✅ An toàn | Novel rõ: LLM frontier chọn mutant trên Defects4J |
**Kết quả:** 3 ✅ / 4 ⚠️ / 0 ❌ → Không có blocker → **CHỌN GAP này** (An toàn nếu downscope: ≥3 dự án Defects4J NHỎ; fallback GPT-4o-mini nếu API quá tốn, ghi rõ trong design-rationale.md).

---

## 1. Dataset
Ý chính là muốn so sánh được với paper thì phải dùng cùng benchmark và cùng mutation tool với paper đó, nếu không thì số liệu không đặt cạnh nhau được. Bảng dưới là dataset và tool chốt cho thí nghiệm, kèm link tải và paper tương ứng để đối chiếu.

| Thành phần | Link tải / nguồn | Phiên bản | Paper dùng chung (đối chiếu) |
|---|---|---|---|
| **Defects4J** (benchmark Java) | https://github.com/rjust/defects4j | v2.0.0 | #3 Jimenez, #4 LEAM++, #5 SODA, #7 LEAM, #8 Seshat, #9 MutationBERT |
| **3 dự án chốt:** `Cli` (commons-cli), `Csv` (commons-csv), `Gson` (gson) | nằm sẵn trong Defects4J (`defects4j checkout -p Cli ...`) | v2.0.0 | #5 SODA và #9 MutationBERT dùng đúng 3 dự án này (trong tập 6: commons-lang, jfreechart, gson, commons-cli, jackson-core, commons-csv), xác nhận tại Zhao_2024 dòng 862–863 và Jain_2023 evidence-table |
| **Major** (mutation tool sinh mutant + kill-matrix) | đóng gói sẵn trong Defects4J (`defects4j mutation`), gốc: https://mutation-testing.org | bundled | #3 Jimenez, #5 SODA, #9 MutationBERT (đều dùng Major) |
| **PIT / PiTest** (mutation tool thay thế) | https://github.com/hcoles/pitest | — | #6 Ojdanic, #8 Seshat (đều dùng PIT) |

**Vì sao đủ để so sánh:**
- 3 dự án `Cli/Csv/Gson` nằm trong tập 6 dự án mà #5 SODA và #9 MutationBERT đã dùng. Vì cùng source code và cùng version Defects4J v2.0.0 nên mutation score nhóm đo được có thể đặt cạnh số của 2 paper này.
- Major đi kèm sẵn trong Defects4J nên nhóm không phải cài tool ngoài, và kill-matrix của nó là deterministic nên dùng làm ground truth (MS_full) được. Đây cũng là tool mà #3, #5, #9 dùng.
- Còn dataset của các paper không chọn (MutantBench của #2, CoREBench/Coreutils của #10, HumanEval của Vy) thì không cần tải, chỉ dùng tới khi muốn mở rộng. Nếu cần thì lấy link artifact ở trang DOI của từng paper.

## 2. Pipeline
Lấy quy trình của #3 Jimenez 2018 (Naturalness) làm khung chuẩn để bám theo, vì paper này làm đúng kiểu cần: chọn X% mutant theo một tiêu chí rồi so với random cùng kích thước, sau đó kiểm định bằng Wilcoxon kèm effect size (xem Jimenez_2018 dòng 188–189 phần quy trình, dòng 249 phần dùng Wilcoxon). Giữ nguyên khung này, chỉ thay bước "chọn theo naturalness (n-gram)" của họ bằng "chọn bằng GPT-4o (temperature=0, zero-shot)".

| Bước | Việc làm | Đầu ra | Mượn từ paper |
|---|---|---|---|
| B1. Chuẩn bị | `defects4j checkout` 3 dự án `Cli/Csv/Gson`, build và chạy test suite gốc cho pass | source + test xanh | #3, #5, #9 (cùng Defects4J v2.0.0) |
| B2. Sinh mutant + ground truth | Chạy Major full mutation trên class mục tiêu để lấy tập mutant M đầy đủ và kill-matrix, từ đó tính ra MS_full | M, MS_full (deterministic) | #3 (Major full), #5/#9 (Major kill-matrix) |
| B3. Chốt kích thước k | Lấy cùng số lượng k mutant cho cả 2 nhánh (Intervention và Comparison) | k cố định / dự án | #3 (so cùng kích thước tập), thiết kế "cùng số lượng" |
| B4. Nhánh I — LLM chọn | Đưa context code và dòng đột biến (diff) cho GPT-4o temp=0 zero-shot để chọn k mutant, có lưu lại prompt và response | tập M_LLM (k mutant) | GAP-T (novel); cách đóng gói mutant+context kế thừa #9 |
| B5. Nhánh C — Random chọn | Random sample k mutant với fixed seed | tập M_random (k mutant) | #3, #10 (random baseline) |
| B6. Tính MS tập con | Chạy test suite trên M_LLM và M_random để lấy MS_LLM, MS_random, đồng thời tính \|MS_subset − MS_full\| | 3 số MS / dự án | #5 (MS error), #9 (MS error) |
| B7. Thống kê | Wilcoxon signed-rank ghép cặp theo dự án, một phía, α=0.05, kèm effect size A₁₂ | p-value, A₁₂ | #3 (Wilcoxon + A₁₂/Vargha-Delaney dòng 475), #10 |
| B8. Metric phụ | Đếm số mutant chạy và thời gian wall-clock (full so với subset) | % effort/time giảm | #6 (số test execution), #4 (giảm số mutant) |
| B9. Kết luận | Bác hoặc không bác H0 dựa theo B7, rồi nhận xét theo Mục 3 | kết luận | — |

**Tính khả thi:** mỗi bước đều dùng đúng một tool miễn phí (Defects4J, Major, PIT), ground truth là deterministic, lại downscope còn 3 dự án nhỏ nên vừa với buffer thời gian (xem phần Feasibility).

## 3. Nhận xét kết quả — căn cứ paper, ngưỡng thành công, kịch bản thất bại

### 3.1 Ngưỡng "thành công" (primary)
- **Tiêu chí chính:** bác được H0, tức MS_LLM > MS_random với Wilcoxon một phía p < 0.05. Nhóm lấy đúng kiểm định mà #3 Jimenez dùng (dòng 249), và cũng là dạng so-với-random của #10 MuDelta. Nói cách khác, vượt được nghĩa là làm được cái mà #3 không làm được, vì ở paper đó naturalness gần như bằng random.
- **Độ lớn hiệu ứng:** A₁₂ tầm 0.57 trở lên. Sở dĩ lấy mốc này vì #3 báo file-level A₁₂ khoảng 0.57–0.58 ở mức chọn 5–25%, đây là mức nhỉnh nhất mà họ đạt. Nếu A₁₂ của nhóm đạt từ 0.57 thì ít nhất LLM cũng ngang điểm tốt nhất của naturalness.

### 3.2 Ngưỡng "giữ được mutation score" (secondary, mô tả)
- |MS_subset − MS_full| ≤ 0.05. Mốc này dựa trên MS error thực nghiệm của #5 SODA là 0.0292 (cross-version) và #9 MutationBERT là 0.02, nên 0.05 là biên khá rộng so với cả hai. Nếu vượt 0.05 thì coi như tập con làm lệch MS nhiều hơn mức mà 2 paper SOTA này chấp nhận. (Con số 0.05 là do nhóm tự chọn cho an toàn chứ không trích thẳng từ paper, nhóm ghi rõ trong design-rationale.)

### 3.3 Đạt kỳ vọng hay không?
- #3 Jimenez đã cho thấy chọn mutant theo naturalness gần như bằng random, tức là không có lợi gì. Dựa vào đó nhóm thấy có hai trường hợp đều có ý nghĩa: (a) nếu MS_LLM > MS_random một cách có ý nghĩa thì đây là đóng góp dương rõ ràng, LLM làm được cái mà n-gram không làm được; (b) nếu MS_LLM xấp xỉ MS_random thì coi như nhóm tái lập lại kết quả âm của #3 nhưng cho LLM, vẫn là một phát hiện có giá trị chứ không phải làm công cốc.

### 3.4 Nếu thất bại
| Kịch bản | Lý do (căn cứ paper) | Bài học | Hướng giải quyết đề xuất |
|---|---|---|---|
| **A. MS_LLM ≈ MS_random** (không ý nghĩa) | Giống kết quả của #3 Jimenez: tín hiệu "tự nhiên/hợp lý" ở mức bề mặt (dù là n-gram hay LLM) không tương quan với mutant khó diệt hay dễ lộ lỗi | Chỉ nhìn code ở dạng zero-shot là chưa đủ | Chuyển sang few-shot hoặc fine-tune có kèm context test giống #9 MutationBERT (mã hoá chung mutant với test, F1 0.79) và #8 Seshat (F-score 0.83), vì 2 paper này thắng baseline là nhờ đưa test vào chứ không zero-shot |
| **B. MS_LLM < MS_random** (LLM tệ hơn) | LLM hay chọn mutant trông "tự nhiên" nên dễ dính phải equivalent mutant, mà #2 LLM-EMD và #6 Ojdanic đều cảnh báo về nhiễu equivalent mutant | Phải lọc equivalent trước khi chấm | Thêm một bước lọc equivalent mutant bằng #2 LLM-EMD (UniXCoder fine-tuned) đặt trước bước B6 |
| **C. API quá tốn / quá chậm** | LLM frontier tốn phí (đã ghi ở Feasibility: Tool/API mức ⚠️) | Chi phí là rào cản thực tế cần lường trước | Dùng phương án dự phòng GPT-4o-mini, giảm k và giảm số class, những cái này nhóm đã ghi trong design-rationale.md |

**Tóm lại:** Xem là thành công khi vừa bác được H0 (p<0.05 ở mục 3.1) vừa giữ được |MS − MS_full| ≤ 0.05 (mục 3.2). Còn nếu rơi vào A, B hoặc C ở mục 3.4 thì xem là thất bại có kiểm soát.
