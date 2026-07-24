# GAP Analysis – AI-assisted Mutation Testing
Evidence table: N = 5 papers | Ngày: 2026-06-03

---

## Bảng GAP tổng quan

| Cột | Phát hiện | Loại GAP | Phản chứng |
|-----|----------|----------|------------|
| Tool/LLM | Mỗi paper dùng AI cho một mục đích riêng lẻ (test generation / mutant generation / equivalent detection / prioritization); không paper nào tích hợp đủ 3 chức năng trong một pipeline | GAP-T | ✅ Kiểm tra 5/5 paper |
| Dataset | Mỗi paper chỉ đánh giá trên một ngôn ngữ/domain duy nhất (Python / JS-TS / Java / Solidity / Kotlin); không có cross-language benchmark | GAP-D | ✅ 5/5 paper xác nhận |
| Metric | 5 paper dùng 5 bộ metric khác nhau (MS, bug-detection, F1, survival-rate+cost, acceptance-rate); không có bộ metric chung | GAP-M | ✅ |
| Hạn chế tự nêu | 5/5 paper đều nhận hạn chế về generalization hoặc dataset nhỏ | GAP-S | ✅ |

---

## GAP Chính: GAP-T

**Phát biểu:** Chưa có nghiên cứu nào đề xuất framework thống nhất tích hợp cả ba chức năng AI vào mutation testing: (1) test generation, (2) mutant prioritization, (3) equivalent mutant detection.

---

## GAP Secondary: GAP-M

**Phát biểu:** Các nghiên cứu dùng metric rất khác nhau khiến không thể so sánh trực tiếp hiệu quả giữa các phương pháp.

---

## Dataset – Link tải & khả năng dùng chung

| Paper | Dataset sử dụng | Link / Nguồn | Có thể dùng chung không? |
|-------|----------------|-------------|--------------------------|
| P1 – MuTAP | HumanEval (164 Python functions); Refactory (1.710 buggy programs) | HumanEval: https://github.com/openai/human-eval · Refactory: https://github.com/githubhuang/Refactory | ✅ HumanEval công khai, dùng được làm benchmark chung |
| P2 – LLMorpheus | 13 JavaScript/TypeScript packages thực tế (có test suite sẵn) | Repo StrykerJS benchmark: https://github.com/nicolo-ribaudo/tc39-proposal-temporal / danh sách trong paper §4.1 | ⚠️ Có thể clone, nhưng cần cài Node.js + StrykerJS |
| P3 – Tian et al. | MutantBench (3.302 mutant pairs, 19 Java programs) | https://github.com/cragkhit/MutantBench | ✅ Công khai, được dùng làm chuẩn cho equivalent mutant detection |
| P4 – PRIMG | Smart contract Solidity từ Code4Arena | https://github.com/code-423n4/code4rena-findings | ⚠️ Công khai nhưng cần Foundry/Hardhat để chạy |
| P5 – Meta ACH | 10.795 lớp Android Kotlin nội bộ Meta | Không công khai | ❌ Không tái tạo được |

**Khuyến nghị:** Dùng **HumanEval (Python)** + **MutantBench (Java)** làm hai benchmark chính — cả hai công khai, được paper P1 và P3 dùng trực tiếp, cho phép so sánh kết quả với số liệu đã công bố.

---

## Pipeline đề xuất (Khả thi – từ chuẩn bị đến kết quả)

```
[Bước 1] Chuẩn bị dữ liệu
  ├── Clone HumanEval → chọn 30–50 Python functions làm PUT (Program Under Test)
  ├── Clone MutantBench → dùng 500 mutant pairs Java làm test bed equivalent detection
  └── Sinh mutant bằng MutPy (Python) hoặc PiTest (Java) → ra danh sách mutant

[Bước 2] Mutant Prioritization (Module 1 – LLM)
  ├── Input: danh sách mutant + source code gốc
  ├── Prompt LLM (Llama-3 8B hoặc GPT-4o-mini) phân loại mutant theo risk score
  └── Output: danh sách mutant xếp hạng ưu tiên

[Bước 3] Test Generation (Module 2 – LLM)
  ├── Input: top-K mutant sau prioritization + code gốc
  ├── Prompt LLM sinh test case (theo chiến lược của MuTAP – P1)
  └── Output: test suite → chạy với pytest / JUnit → lọc test pass

[Bước 4] Equivalent Mutant Detection (Module 3 – Embedding)
  ├── Input: mutant survived sau bước 3
  ├── Dùng fine-tuned UniXcoder / CodeT5+ (theo P3) classify equivalent/non-equivalent
  └── Output: nhãn equivalent → loại khỏi kết quả, báo cáo precision/recall

[Bước 5] Đánh giá kết quả
  ├── Metric chính: Mutation Score trên HumanEval (so sánh với P1: baseline 93,57%)
  ├── Metric phụ: F1 equivalent detection (so sánh với P3: baseline 81,88%)
  └── Báo cáo: kích thước test suite, thời gian chạy, chi phí API (nếu dùng)
```

**Điểm khả thi:**
- Colab/CPU đủ cho Llama-3 8B (quantized) hoặc dùng GPT-4o-mini API (~$2–5 cho toàn bộ HumanEval)
- MutPy và PiTest đều có pip/Maven package
- MutantBench và HumanEval không cần license

---

## Feasibility Check – GAP Chính

| Tiêu chí | Mức | Ghi chú cụ thể |
|----------|-----|---------------|
| Dataset | ✅ | HumanEval (GitHub OpenAI) + MutantBench (GitHub) – công khai, dùng chung với P1, P3 |
| Tool/API | ⚠️ | Llama-3 8B (quantized, miễn phí) hoặc GPT-4o-mini (≤ $5); MutPy / PiTest miễn phí |
| Compute | ✅ | Colab T4 đủ cho Llama-3 8B Q4; CPU đủ cho MutPy trên HumanEval |
| Ground truth | ⚠️ | MutantBench có nhãn equivalent; HumanEval cần tự sinh mutant → cần verify thủ công mẫu |
| Pipeline tích hợp | ⚠️ | 3 module độc lập cần JSON interface chuẩn; risk khi kết nối |
| Thời gian | ⚠️ | 30–50 PUT Python + 500 mutant Java: ước tính 3–4 tuần implement + eval |
| Contribution | ✅ | Là paper đầu tiên tích hợp đủ 3 chức năng trên benchmark công khai, so sánh trực tiếp với P1 và P3 |

**Kết quả tổng:** ⚠️ Khả thi nhưng cần quản lý scope chặt – ưu tiên 2 benchmark cố định, không mở rộng sang Solidity hay Kotlin trong phạm vi nghiên cứu này.
