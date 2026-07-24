# Gap Statement Final — AI/ML/LLM-Based Mutation Testing

Evidence table merged: **N = 34 papers** (Đã gộp và loại bỏ trùng lặp từ tất cả thành viên).

## 1. Các khoảng trống phát hiện (GAPs)

### GAP-T (Technology): Thiếu nghiên cứu trực tiếp về LLM-based mutant ranking/selection trên Java mutation testing
**Bằng chứng:** [Cột Tool/LLM] — Merged evidence table cho thấy AI/ML/LLM đã được áp dụng vào mutation testing theo nhiều hướng khác nhau, nhưng trọng tâm còn phân tán:
- **LLM-based mutant generation / semantic mutation:** Wang et al. (2025), SMART, LLMorpheus, MuTAP.
- **LLM-based / mutation-guided test generation:** MUTGEN, Dakhel, Foster (ACH), PRIMG.
- **Equivalent mutant detection (EMD):** GEM-LLM, LLM-EMD.
- **Predictive mutation testing (PMT) / kill prediction:** Seshat, MutationBERT, SODA, AL-PMT, WITNESS.
- **Learning-based mutant construction / selective mutation:** LEAM, LEAM++.

Các hướng này có liên quan đến mutation testing, nhưng không trực tiếp trả lời câu hỏi cốt lõi của nhóm: **LLM (theo phương pháp Zero-shot) có thể xếp hạng và chọn lọc (ranking/select) mutant để giảm số lượng cần chạy, so với baseline chọn ngẫu nhiên (random fixed-seed), trong khi vẫn giữ được hiệu quả phát hiện lỗi hay không?** 
Khoảng trống công nghệ chính là sự thiếu vắng đánh giá trực tiếp **LLM-based mutant ranking/selection** như một can thiệp (intervention) độc lập.

### GAP-M (Metric): Metric đánh giá phân tán; thiếu đo đạc đồng thời effort reduction và mutation effectiveness
**Bằng chứng:** [Cột Metric và Kết quả] — Các bài báo sử dụng nhiều nhóm metric khác nhau: F1-score, ROC-AUC, real bug detection rate, compilability rate, v.v. 
Tuy nhiên, chưa có nghiên cứu nào báo cáo đồng thời theo đúng cấu trúc thực tiễn: (1) giảm bao nhiêu effort/số mutant cần chạy; (2) mutation score giữ lại được bao nhiêu; và (3) so sánh trực tiếp với **random mutant selection**. Nếu chỉ đo F1 hay AUC thì chưa đủ để kết luận LLM-based ranking có thực sự mang lại "cost-effectiveness" trong thực tế hay không.

### GAP-D (Dataset): Thiếu kiểm chứng LLM-based ranking trên đúng setting Java/Defects4J
**Bằng chứng:** [Cột Dataset] — Mặc dù Defects4J xuất hiện nhiều trong các bài về PMT, nhưng các nghiên cứu áp dụng LLM frontier lại thường thực hiện trên các domain khác như Python (MuTAP), Solidity (PRIMG), JavaScript (LLMorpheus) hoặc Kotlin (ACH). Chưa có bằng chứng rõ ràng cho LLM-based mutant ranking trên Java/Defects4J đối đầu với random baseline.

### GAP-C (Cost vs. Quality trade-off): Thiếu đánh giá trực tiếp sự đánh đổi
**Bằng chứng:** [Cột Kết quả & Hạn chế] — Một số bài báo có nhắc đến việc giảm effort (như LEAM++ giảm 17.5% mutant, hay AL-PMT), nhưng chúng dựa trên learning-based construction hoặc active learning, không phải LLM-based ranking. Khoảng trống rõ rệt là việc đánh giá sự đánh đổi (trade-off) trong cùng một pipeline: **giảm chi phí** đi kèm **giữ vững chất lượng**.

---

## 2. GAP Nhóm được chọn

*   **Primary GAP (GAP Chính):** Thiếu bằng chứng trực tiếp về việc sử dụng **LLM-based mutant ranking/selection** (Zero-shot) để giảm số lượng mutant cần thực thi trong Java mutation testing, so với hệ quy chiếu **Random Selection**, trong khi vẫn duy trì chất lượng kiểm thử (mutation adequacy).
*   **Supporting GAPs (GAP Hỗ trợ):** Thang đo (Metric) hiện tại phân tán, chưa đo đồng thời sự đánh đổi Cost-Quality; và các nghiên cứu LLM mạnh hiện nay chưa tập trung vào benchmark Java/Defects4J cho bài toán chọn lọc.

---

## 3. Phát biểu GAP Tổng hợp (Dùng cho Proposal)

> "Mặc dù các nghiên cứu hiện tại đã chứng minh AI và LLM có thể hỗ trợ mutation testing ở nhiều khía cạnh như sinh mutant (generation), phát hiện mutant tương đương (EMD) hay sinh test case, bức tranh nghiên cứu vẫn còn phân tán về công nghệ và thang đo. Cụ thể, qua khảo sát 34 bài báo, chưa có nghiên cứu nào đánh giá trực tiếp khả năng của LLM trong việc tự động xếp hạng và chọn lọc mutant (mutant ranking/selection) như một can thiệp độc lập trên nền tảng Java/Defects4J. Hơn nữa, thiếu vắng các đánh giá đồng thời về khả năng giảm thiểu chi phí (effort reduction) và việc duy trì hiệu quả phát hiện lỗi (mutation adequacy) so với phương pháp chọn ngẫu nhiên. Vì vậy, nghiên cứu này nhằm lấp đầy khoảng trống bằng cách kiểm chứng năng lực 'Zero-shot' của LLM trong việc tối ưu hóa chi phí mutation testing, đồng thời thiết lập các ngưỡng thực nghiệm rõ ràng cho sự đánh đổi giữa chi phí và chất lượng."
