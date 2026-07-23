# Proposal Amendment [v1.0 -> v1.1]

**Nhóm:** Nhóm 3
**Ngày:** 2026-07-08
**Phát hiện từ:** Tuần 8 full experiment (không phải Tuần 7 pilot — bug này chỉ lộ ra khi đối chiếu số
group của Lang (739) với Math (18) trong `results/paired_mutation_scores.csv`)

**Phát hiện vấn đề kỹ thuật:** PIT đã chạy Commons Math ở **scope hẹp hơn nhiều** so với Commons Lang:

- Lang: `target_mode=full`, `source_xml` trỏ tới batch `results_full20` → ~147 class/version → 739
  (project,version,class_name) group.
- Math: cùng cách chạy nhưng chỉ ra ~1 class/version dù đã chạy đủ 10 version (1f–10f) → chỉ 18 group.

Xác nhận bằng cột `source_xml` trong `data/full_ground_truth.csv` (không phải suy đoán). Hệ quả: so sánh
GPT-vs-Random **trong từng project riêng lẻ** vẫn hợp lệ (cùng pool cho cả 2 nhánh), nhưng dùng Math để
kết luận về **generalization giữa hai project** (Lang vs Math) thì chưa công bằng, vì n_group của Math quá
nhỏ và không phải mẫu đại diện (đây là 100% những gì pipeline hiện có, không phải một subsample).

---

## Thay đổi đề xuất

| Mục | Proposal v1.0 | Đề xuất v1.1 | Lý do kỹ thuật |
|---|---|---|---|
| §5.2 Dataset (Preprocessing, Commons Math) | Không ghi rõ PIT phải chạy ở scope nào (class/version) cho từng project | Chạy lại PIT cho Commons Math ở **scope rộng** (`target_mode=full`, cùng cấu hình đã dùng cho Lang) trên **5 version chốt trước**: `1f, 2f, 3f, 4f, 5f` (chọn theo số thứ tự version tăng dần — quy tắc cố định, không phụ thuộc kết quả, để tránh p-hacking) | Đảm bảo Math có đủ (project,version,class_name) group để so sánh generalization công bằng với Lang; downscope 5/10 version (không phải toàn bộ 10) vì giới hạn Kaggle 9–12h/session (đã có tiền lệ ở §8.4 Contingency Plan: "Giảm số versions/classes") |
| §5.1 Step 2 (Generate mutants) | Không phân biệt scope PIT giữa các project | Ghi rõ: mọi project phải chạy PIT ở cùng `target_mode` để đảm bảo so sánh công bằng giữa các project | Tránh lặp lại lỗi tương tự cho project khác trong tương lai |
| §4 RQ, §5.4 Metric, §6.1 Statistical Test, §6.3 Sub-group rule | — | **Không đổi** | Không phải lỗi kỹ thuật, không được đổi theo §6.5 HARKing prevention |

## Sections bị ảnh hưởng

- [x] §5.2 Dataset (Preprocessing)
- [ ] §4 Research Questions — không đổi
- [ ] §6 Evaluation Plan — không đổi
- [ ] §8 Timeline & Resources — thêm 1 dòng công việc (rerun Math), không đổi phân công vai trò

**Đính kèm:** `RT-SWT-003-nhom3-Tuan8/notes.md` (mục 4), `results/paired_mutation_scores.csv`,
`results/summary.csv`

**Xin phê duyệt GV:** [ ] Chưa nộp — Ngày: ___________

---

## Kế hoạch thực hiện chi tiết (sau khi GV duyệt)

> Nguyên tắc: chốt N=5 version **trước khi chạy**, không chạy thêm/bớt version sau khi thấy kết quả đẹp
> hay xấu. Nếu 5 version không đủ build/test được, downscope tiếp theo quy tắc §8.4 (không phải vì
> "kết quả không đẹp").

### Bước 1 — Chốt scope kỹ thuật (DG)
1. Xác nhận 5 version Math sẽ chạy lại: `1f, 2f, 3f, 4f, 5f`.
2. Với mỗi version, checkout + build + chạy test suite gốc trước khi mutate (giống §5.2 Preprocessing).
3. Ghi lại version nào build được / build lỗi vào `notes.md` (nếu có version lỗi, downscope và ghi lý do
   kỹ thuật cụ thể — không thay bằng version khác chỉ vì tiện).

### Bước 2 — Chạy lại PIT scope rộng trên Kaggle (DG)
1. Chạy PIT với `target_mode=full` (giống cấu hình đã dùng cho Lang `results_full20`) cho 5 version đã
   chốt.
2. Lưu report ra `mutations.xml` cho từng version, tổng hợp thành CSV có cùng schema với
   `data/full_ground_truth.csv` hiện tại (cột: `detected, status, ..., project, version, target_mode,
   source_xml, local_index, killed, mutant_id`).
3. Do session Kaggle giới hạn ~9–12h: nếu 1 version không chạy hết trong 1 session, chia nhỏ theo class và
   nối checkpoint lại (giống cách đã làm với Lang).

### Bước 3 — Cập nhật dataset (DG)
1. Giữ nguyên toàn bộ dòng Lang trong `data/full_ground_truth.csv` và `data/full_sample.csv`.
2. Với Math: **xoá** các dòng Math cũ (18 group scope hẹp) và **thay** bằng dữ liệu Math mới (scope rộng,
   5 version). Không gộp cũ+mới (tránh trộn 2 scope khác nhau trong cùng phân tích).
3. Mutant ID mới phải theo đúng format hiện có: `{project}_{version}_full_{index}` (xem ví dụ
   `Math_1f_full_1` trong `data/full_ground_truth.csv` hiện tại) để tương thích với toàn bộ pipeline không
   cần sửa code.
4. Chạy `scripts/validate_mutant_pool.py` trên `data/full_sample.csv` mới → phải `Status: VALID`.

### Bước 4 — GPT ranking chỉ cho mutant Math mới (LR)
1. **Không gọi lại API cho mutant Lang / Math cũ** — checkpoint hiện có (`results/full_gpt_checkpoint.jsonl`)
   đã có đủ Lang; chỉ mutant Math mới chưa có trong checkpoint sẽ được `run_gpt_ranking.py` tự động gọi
   (script đã có logic resume: `pending_df = df[~df["mutant_id"].isin(done_ids)]`).
2. Log API mới nối tiếp vào `results/full_api_log.txt` / `results/full_cost_log.csv` (không ghi đè).
3. Cập nhật ước tính chi phí trong `notes.md` (số mutant mới × ~$0.007/mutant, theo §8.2 proposal).

### Bước 5 — Random baseline cho Math mới (MS)
1. Chạy `scripts/random_baseline.py` lại (seed=42 giữ nguyên) — script tự tính lại cho toàn bộ pool mới
   (bao gồm Lang không đổi + Math mới), không cần sửa code.

### Bước 6 — Reselect theo group đúng (LR/MS)
1. Chạy `scripts/reselect_by_group.py` (group_columns = project+version+class_name, đã đúng từ Bug 2) để
   sinh lại `results/full_gpt_selected.csv` / `results/full_random_selected.csv`.
2. Kiểm tra: số group Math trong output phải bằng số (project,version,class_name) group thật có trong Math
   mới (kỳ vọng > 18, tuỳ số class/version thực tế sau khi chạy scope rộng).

### Bước 7 — Tính lại metric + thống kê (MS)
1. Chạy `scripts/compute_metric.py` → cập nhật `results/summary.csv`, `results/paired_mutation_scores.csv`.
2. Chạy lại `results/full_analysis.ipynb` từ đầu (Restart & Run All) → cập nhật `figures/fig1_distribution.png`,
   `figures/fig2_comparison.png`.
3. Không đổi test/threshold dù kết quả Math mới ra sao (§6.5 HARKing prevention).

### Bước 8 — Báo cáo trung thực (RW/PL)
1. Cập nhật `notes.md` mục 3–4 với số liệu Math mới, xoá/replace phần "threat to validity chưa xử lý" nếu
   đã giải quyết được, hoặc ghi rõ nếu vẫn còn giới hạn (vd 5 version vẫn ít hơn Lang).
2. Báo cáo cả 3 khả năng: Math vẫn không ủng hộ H1 (negative result vẫn hợp lệ, viết đúng §6.4 — không
   viết "GPT4o-mini vô dụng"), Math ủng hộ H1 (Case 1/2/3 tuỳ p-value/effect size), hoặc không đủ n_group
   để chạy test riêng (< 10 group, khi đó chỉ báo cáo descriptive theo §6.3).
3. Commit toàn bộ thay đổi lên GitHub theo checklist RBL-4 (mỗi batch lớn commit ngay, message có ý nghĩa).
