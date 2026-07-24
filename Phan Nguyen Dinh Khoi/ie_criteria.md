# IE Criteria — Mutation Testing Enhancement with AI (SE1903)

> Bộ tiêu chí YES/NO để quyết định giữ hay loại paper. Đã chỉnh theo đúng đề tài
> (AI-guided mutant selection vs random mutant generation trên Java projects).

## Inclusion Criteria (IC) — phải YES hết

- **IC1 (Language):** Paper viết bằng tiếng Anh.
- **IC2 (Timeline):** Xuất bản từ **2018 đến nay** (theo mốc trong hướng dẫn).
- **IC3 (Peer-reviewed):** Conference hoặc Journal có phản biện.
- **IC4 (Context):** Nội dung về **AI / Machine Learning / Deep Learning / search-based /
  evolutionary techniques để hướng dẫn việc CHỌN, GIẢM, hoặc ƯU TIÊN mutants** trong mutation
  testing (đây là Intervention I); HOẶC về **random mutant selection/generation** dùng làm
  Comparison (C).
- **IC5 (Empirical):** Có kết quả thực nghiệm bằng số (không chỉ survey/opinion/position paper).

## Exclusion Criteria (EC) — loại nếu YES với bất kỳ EC nào

- **EC1 (Duplicate):** Đã có trong danh sách (trùng paper).
- **EC2 (Access):** Không tải được full-text.
  ⚠ **Lưu ý quan trọng:** Ở vòng 1 (title+abstract) tôi KHÔNG dùng EC2 vì các file RIS đã có
  sẵn abstract. EC2 chỉ áp dụng ở vòng 2 khi bạn thực sự đi tải PDF mà không lấy được.
- **EC3 (Short):** Poster, extended abstract, tool-competition report, hoặc < 4 trang.
- **EC4 (Scope):** **Mutation testing OF deep-learning/ML systems** (áp mutation LÊN mô hình ML —
  KHÁC với dùng AI để hướng dẫn chọn mutants); HOẶC chỉ về test-case generation, fault
  localization, requirements, smart-contract/BPEL/DOM operators, v.v. — không phải AI-guided
  mutant selection vs random.

---

## ⚠ Hai điểm cần bạn tự quyết định (tôi nêu rõ, không tự ý chốt thay bạn)

1. **Mốc IC2 = 2018.** Mốc này lấy từ template hướng dẫn. Nhưng các paper NỀN TẢNG về
   "random mutant selection" lại cũ hơn:
   - Zhang et al. 2010 — *Is operator-based mutant selection superior to random?* (ICSE)
   - Zhang et al. 2013 — *Operator-based and random mutant selection: Better together* (ASE)
   - McCurdy et al. 2016 — *mrstudyr* (ICSME)
   - Delamaro et al. 2014 — *Growing a Reduced Set of Mutation Operators* (SBES)

   Hiện tôi **loại** chúng theo IC2 (đúng template). Nếu cô cho phép, bạn có thể nới IC2 để
   GIỮ riêng nhóm "C = random" làm baseline kinh điển. → Cần bạn xác nhận với giảng viên.

2. **EC4 với nhóm "MT of Deep Learning".** String A kéo về rất nhiều paper kiểu DeepMutation,
   DeepCrime, DeepWeak, TF-DM, RLMutation... Đây là *mutation testing ÁP DỤNG cho hệ DL*, KHÁC
   hẳn đề tài của bạn (*dùng AI để chọn mutants cho code Java*). Tôi loại theo EC4. Đây là khác
   biệt then chốt — đừng nhầm 2 hướng này.
