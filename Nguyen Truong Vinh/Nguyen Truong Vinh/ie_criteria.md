# Inclusion / Exclusion Criteria — Mutation Testing Enhancement with AI
**Thành viên:** Nguyễn Trường Vinh
**RQ:** "Khi chọn cùng số lượng mutant như random sampling, GPT-4o (temperature=0, zero-shot) có giữ được mutation score cao hơn random trên các dự án Java của Defects4J hay không?"
**PICO:** P: Chương trình Java từ Defects4J (≥3 dự án), mutant sinh bởi PIT/Major | I: GPT-4o (temperature=0) zero-shot chọn tập con mutant | C: Random mutant sampling cùng số lượng (fixed seed) | O: Metric 1 (chính): mutation score tập LLM so với tập random; Metric 2 (phụ): % thời gian/mutant tiết kiệm so với full, chênh lệch |MS_chọn − MS_full| mong muốn ≤ 0.05
## Inclusion Criteria (IC) — phải YES hết
- **IC1 (Language):** Viết bằng tiếng Anh
- **IC2 (Timeline):** Xuất bản từ 2018 đến nay
- **IC3 (Peer-reviewed):** Đăng ở conference / journal có phản biện
- **IC4 (Context):** Về mutation testing VÀ có dùng kỹ thuật AI/ML/DL/LLM tác động lên mutant (chọn, giảm, dự đoán, hoặc sinh mutant)
- **IC5 (Empirical):** Có kết quả thực nghiệm bằng số (không chỉ survey/opinion)

## Exclusion Criteria (EC) — loại nếu YES bất kỳ
- **EC1 (Duplicate):** Đã có trong danh sách (trùng paper)
- **EC2 (Access):** Không tải được full-text PDF
- **EC3 (Short):** Poster, extended abstract, hoặc < 4 trang
- **EC4 (Scope):** Ngoài phạm vi: mutation testing không dùng AI, HOẶC AI chỉ là hệ-thống-được-test (không dùng để xử lý mutant)
